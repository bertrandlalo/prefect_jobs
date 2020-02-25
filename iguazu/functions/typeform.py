from collections import deque
from functools import partial
from typing import Dict, List
import json
import logging
import pkg_resources

from requests import codes, request
import numpy as np
import pandas as pd
import pendulum


logger = logging.getLogger(__name__)


def _clip_page_size(size, min_value, max_value):
    return max(min_value, min(size, max_value))


def _get_default_header(token):
    return {
        'Content-Type': 'text/plain',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Authorization': f'Bearer {token}',
    }


def fetch_responses(url: str, form_id: str, token: str, page_size: int = 1000) -> List[Dict]:
    page_size = _clip_page_size(page_size, 100, 1000)
    url = f'{url}/forms/{form_id}/responses'
    params = dict(page_size=page_size)
    payload = {}
    headers = _get_default_header(token)

    before = None
    by_token = dict()
    while True:
        if before is not None:
            params['before'] = before
        logger.debug('Requesting next %d responses', page_size)
        response = request('GET', url=url, params=params, headers=headers, data=payload)

        if response.status_code != codes.ok:
            logger.warning('Request to fetch responses failed with code %d: %s',
                           response.status_code, response.text)
            raise RuntimeError('Failed to communicate with typeform server')

        r = response.json()
        total = r.get('total_items', 0)
        items = r.get('items', [])
        if total == 0 or not items:
            logger.debug('No more results available')
            break
        else:
            logger.debug('Processing %d candidate items, there are still %d to process',
                         len(items), total - len(items))

        last = items[-1]
        before = last['token']
        n_dropped = 0
        for item in items:
            token = item['token']
            if item['answers'] is None or token in by_token:
                n_dropped += 1
                continue
            by_token[token] = item

    logger.info('Retrieved %d valid  responses', len(by_token))
    return list(by_token.values())


def fetch_form(url: str, form_id: str, token: str) -> Dict:
    url = f'{url}/forms/{form_id}'
    params = {}
    payload = {}
    headers = _get_default_header(token)

    logger.debug('Requesting form %s details', form_id)
    response = request('GET', url=url, params=params, headers=headers, data=payload)
    if response.status_code != codes.ok:
        logger.warning('Request to fetch form details failed with code %d: %s',
                       response.status_code, response.text)
        raise RuntimeError('Failed to communicate with typeform server')

    return response.json()


def answers_to_dataframe(response: Dict) -> pd.DataFrame:

    converters = {
        'boolean': partial(_generic_parse, key='boolean', func=bool),
        'choice': partial(_generic_parse, key='choice', func=lambda x: x['label']),
        'choices': partial(_generic_parse, key='choices', func=lambda x: x['labels']),
        'number': partial(_generic_parse, key='number', func=float),
        'text': partial(_generic_parse, key='text', func=str),
        'phone_number': partial(_generic_parse, key='phone_number', func=str),
        'email': partial(_generic_parse, key='email', func=str),
        'date': partial(_generic_parse, key='date', func=lambda x: pendulum.parse(x).isoformat())
    }
    answers = response['answers']
    hidden = response.get('hidden', None)

    all_records = []
    for ans in answers:
        record = {}
        field = ans['field']
        for fi in field:
            record[f'field_{fi}'] = field[fi]

        ans_type = ans['type']
        record['type'] = ans_type
        if ans_type not in converters:
            raise ValueError(f'Parsing an answer of type "{ans_type}" is not implemented')
        record['value'] = converters[ans_type](ans)
        all_records.append(record)

    dataframe = pd.DataFrame.from_records(all_records)
    if hidden:
        for k, v in hidden.items():
            if k in dataframe.columns:
                raise RuntimeError('Hidden values cannot be an existing column')
            dataframe.insert(0, k,  v)

    return dataframe


def add_form_config(dataframe: pd.DataFrame, form: Dict) -> pd.DataFrame:
    # Process form information from API response
    fields = []
    fields_queue = deque(form['fields'])
    while fields_queue:
        f = fields_queue.popleft()
        fdict = {'field_ref': f['ref']}
        properties = f.get('properties', {})
        if f['type'] == 'opinion_scale':
            fdict['steps'] = properties['steps']
            fdict['start_at_one'] = properties['start_at_one']
        fields.append(fdict)

        if f['type'] == 'group':
            fields_queue.extend(properties['fields'])

    df_fields = pd.DataFrame.from_records(fields)

    # Obtain manual config from resources CSV file
    form_id = form['id']
    resource_name = f'typeforms/{form_id}/fields.csv'
    logger.debug('Trying to find resource on %s named %s', __name__, resource_name)
    form_config = dataframe[['field_ref']]  # dummy dataframe that would join without problems
    try:
        stream = pkg_resources.resource_stream(__name__, resource_name)
        form_config = pd.read_csv(stream)
        logger.debug('Got form config:\n%s', form_config.to_string())
        form_config['value_map'] = form_config['value_map'].apply(lambda s: json.loads(s) if not pd.isnull(s) else None)
    except FileNotFoundError:
        logger.warning('Could not find resource %s necessary to obtain the '
                       'configuration of form %s', resource_name, form_id,
                       exc_info=True)

    merged = (
        dataframe
        .merge(df_fields, on='field_ref', how='left')
        .merge(form_config, on='field_ref', how='left')
    )

    return merged


def calculate_scores(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()  # type: pd.DataFrame

    # Manage values from value maps first
    idx_with_value_map = ~df['value_map'].isnull()
    logger.debug('Converting values using a value_map of %d answers',
                 idx_with_value_map.sum())
    df.loc[idx_with_value_map, 'value'] = (
        df.loc[idx_with_value_map, ['value', 'value_map']]
        .apply(lambda row: row.value_map.get(row.value, np.nan), axis='columns')
    )
    df.loc[idx_with_value_map, 'type'] = 'number'  # Now these are regular numbers

    # Manage simple value=score case
    idx_numbers = (df['type'] == 'number')
    df['score'] = np.nan
    df.loc[idx_numbers, 'score'] = pd.to_numeric(df.loc[idx_numbers, 'value'])

    # Manage reversed scores
    idx_reversed = df['reversed'].dropna().astype(bool)
    logger.debug('Reversing scores on %d answers', (idx_numbers & idx_reversed).sum())
    df.loc[idx_numbers & idx_reversed, 'score'] = (
        df.loc[idx_numbers & idx_reversed]
        # reverse range from [a,b] to [b,a] by doing: (a + b) - x
        # where a is either 0 or 1, and b is the number of steps
        .apply(lambda row: int(row.start_at_one) + int(row.steps) - row.score, axis='columns')
    )

    # Select only the useful columns and rows
    df = df.loc[
        ~df.domain.isnull(),  # Values without domain are not useful
        ['id', 'field_ref', 'domain', 'dimension', 'value', 'score']
    ]

    return df


def _generic_parse(answer, *, key, func):
    if key not in answer:
        logger.warning('Could not parse %s in %s, returning None', key, answer)
        return None
    return func(answer[key])

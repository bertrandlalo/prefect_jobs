import logging
from collections import deque
from functools import partial
from typing import Dict, List

import pendulum
from numpy import clip
from requests import codes, request

logger = logging.getLogger(__name__)


def _get_default_header(token):
    return {
        'Content-Type': 'text/plain',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Authorization': f'Bearer {token}',
    }


def fetch_responses(url: str, form_id: str, token: str, page_size: int = 1000) -> List[Dict]:
    """ Download all responses of a typeform form using the typeform API

    Parameters
    ----------
    url
        URL of the typeform API.
    form_id
        Identifier of the typeform form.
    token
        Authentication token for the typeform API.
    page_size
        Page size to use when downloading responses.

    Returns
    -------
    A list with all responses as dictionaries.

    Notes
    -----
    The schema of the response is available at
    https://developer.typeform.com/responses/

    """
    page_size = clip(page_size, 100, 1000)
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


def get_form_fields(form: Dict) -> Dict:
    # Since fields can be recursive (when the type is "group"), the following
    # code is an iterative version of a breath-first search on these fields,
    # in order to to visit them all.
    fields = dict()
    fields_queue = deque(form['fields'])
    while fields_queue:
        f = fields_queue.popleft()
        fid = f['ref']
        fields[fid] = f
        if f['type'] == 'group':
            properties = f.get('properties', {})
            fields_queue.extend(properties.get('fields', []))
    return fields


def get_response_fields(response: Dict) -> Dict:
    fields = {
        answer['field']['ref']: answer
        for answer in response.get('answers', [])
    }
    return fields


def _generic_parse(answer, *, key, func):
    if key not in answer:
        logger.warning('Could not parse %s in %s, returning None', key, answer)
        return None
    return func(answer[key])


PARSERS = {
    'boolean': partial(_generic_parse, key='boolean', func=bool),
    'choice': partial(_generic_parse, key='choice', func=lambda x: x['label']),
    'choices': partial(_generic_parse, key='choices', func=lambda x: x['labels']),
    'number': partial(_generic_parse, key='number', func=float),
    'text': partial(_generic_parse, key='text', func=str),
    'phone_number': partial(_generic_parse, key='phone_number', func=str),
    'email': partial(_generic_parse, key='email', func=str),
    'date': partial(_generic_parse, key='date', func=lambda x: pendulum.parse(x).isoformat())
}


def parse_answer(answer):
    answer_type = answer['type']
    if answer_type not in PARSERS:
        raise NotImplementedError(f'Parsing an answer of type "{answer_type}" is not implemented')
    value = PARSERS[answer_type](answer)
    return value

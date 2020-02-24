from typing import Dict, List, Optional
import logging

from requests import codes, request


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

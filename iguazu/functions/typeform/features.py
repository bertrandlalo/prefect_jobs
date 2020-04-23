from typing import Dict

import pandas as pd
from dsu.pandas_helpers import reorder_columns

from iguazu.functions.typeform.schemas import get_form_config


def extract_features(form: Dict, response: Dict) -> pd.DataFrame:
    form_id = form['id']
    form_config = get_form_config(form_id)
    features_dict = form_config.collect_features(form, response)
    user_hash = response.get('hidden', {}).get('id', None)
    response_id = response.get('response_id', None)

    # Assumming features_dict is something like:
    # {'name': {'value': 123, 'type': 'dimension'}, 'other': {'value': 456, 'type': 'domain'}}
    # then the following operations will transform to a spec-valid feature dataframe:
    dataframe = (
        # 1..from_dict will convert to a dataframe like:
        #        value       type
        # name     123  dimension
        # other    456     domain
        pd.DataFrame.from_dict(features_dict, orient='index')
        # 2. renaming the index and the columns will make the correct columns as:
        #       id  value      level
        # 0   name    123  dimension
        # 1  other    456     domain
        .rename_axis(index='id')
        .rename(columns={'type': 'level'})
        .reset_index(drop=False)
        # 3. add new "fixed" columns by adding the reference, user_hash and response_id
        #       id  value      level  reference  user_hash  response_id
        # 0   name    123  dimension    subject     blabla         xxxx
        # 1  other    456     domain    subject     blabla         xxxx
        .assign(reference='subject',
                user_hash=user_hash,
                response_id=response_id)
    )
    # Reorder columns to have id, value, reference first
    return reorder_columns(dataframe,
                           'id', 'value', 'reference', ...)

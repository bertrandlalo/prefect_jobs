from typing import Dict

import pandas as pd

from iguazu.functions.typeform.schemas import get_form_config


def extract_features(form: Dict, response: Dict) -> pd.DataFrame:
    form_id = form['id']
    form_config = get_form_config(form_id)
    features_dict = form_config.collect_features(form, response)
    user_hash = response.get('hidden', {}).get('id', None)

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
        #       id  value  reference
        # 0   name    123  dimension
        # 1  other    456     domain
        .rename_axis(index='id')
        .rename(columns={'type': 'reference'})
        .reset_index(drop=False)
        # 3. add a new column by adding the user_hash
        #       id  value  reference user_hash
        # 0   name    123  dimension    blabla
        # 1  other    456     domain    blabla
        .assign(user_hash=user_hash)
    )
    return dataframe

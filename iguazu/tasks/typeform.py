import collections
import json
import pathlib
from typing import Dict, List, Optional
from urllib.parse import urlparse

import pandas as pd
import prefect
from prefect.client import Secret

import iguazu
from iguazu.core.exceptions import PreconditionFailed
from iguazu.core.files import FileAdapter, LocalFile, QuetzalFile
from iguazu.functions.typeform import (
    add_form_config, answers_to_dataframe, fetch_form, fetch_responses,
    calculate_scores
)


DEFAULT_BASE_URL = 'https://api.typeform.com'


class _BaseTypeformAPITask(iguazu.Task):

    def __init__(self, *,
                 form_id: str,
                 base_url: str = DEFAULT_BASE_URL,
                 token_secret: str = 'TYPEFORM_TOKEN',
                 **kwargs):
        super().__init__(**kwargs)
        self._form_id = form_id
        self._base_url = base_url
        self._token_secret = token_secret

    def run(self, **kwargs):
        raise NotImplementedError('Do not use this class directly, '
                                  'extend it and implement its run method')

    def preconditions(self, **inputs):
        super().preconditions(**inputs)
        if self._base_url is None:
            raise PreconditionFailed('base_url must not be None')
        if self._form_id is None:
            raise PreconditionFailed('form_id must not be None')

        url = urlparse(self._base_url)
        if url.scheme != 'https':
            raise PreconditionFailed('base_url must be a https address')

    @property
    def token(self):
        return str(Secret(self._token_secret).get())


class FetchResponses(_BaseTypeformAPITask):

    def run(self, **kwargs) -> List[Dict]:
        self.logger.info('Requesting typeform responses of form %s at address %s',
                         self._form_id, self._base_url)
        responses = fetch_responses(self._base_url, self._form_id, self.token)
        responses = responses[:3]
        self.logger.info('Obtained %d responses', len(responses))
        return responses


class GetForm(_BaseTypeformAPITask):

    def run(self, **kwargs) -> Dict:
        self.logger.info('Requesting form %s at address %s',
                         self._form_id, self._base_url)

        form = fetch_form(self._base_url, self._form_id, self.token)
        return form


class GetUserHash(iguazu.Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, *, response: Dict) -> str:
        hidden_field = response.get('hidden', {})
        user_hash = hidden_field.get('id', None)
        return user_hash


class Save(iguazu.Task):

    def __init__(self, form_id: str, **kwargs):
        super().__init__(**kwargs)
        self.form_id = form_id

    def run(self, *,
            response: Dict,
            response_id: str) -> Optional[FileAdapter]:

        output = self.default_outputs(response=response, response_id=response_id)
        self.logger.info('Saving response to %s', output)

        with output.file.open(mode='w') as f:
            json.dump(response, f, indent=2, sort_keys=True)

        return output

    def preconditions(self, **inputs):
        super().preconditions(**inputs)
        if self.form_id is None:
            raise PreconditionFailed('form_id must not be None')

    def default_outputs(self, *, response_id, **kwargs) -> Optional[FileAdapter]:
        filename = pathlib.Path('typeform') / self.form_id / response_id / 'responses.json'
        file = self.create_file(
            parent=None,
            filename=filename.name,
            path=str(filename.parent),
            temporary=False
        )
        return file


class ExtractScores(iguazu.Task):

    def run(self, *, response: Dict, form: Dict) -> pd.DataFrame:
        df_answers = answers_to_dataframe(response)
        df_extended, domain_config = add_form_config(df_answers, form)
        df_scores = calculate_scores(df_extended)
        self.logger.info('Extracted typeform answers and scores:\n%s',
                         df_scores.to_string())
        return df_scores


class Report(iguazu.Task):

    def run(self, *, files):
        status = []
        journal_family = self.meta.metadata_journal_family
        for f in files:
            meta = f.metadata.get(journal_family, {})
            journal_status = meta.get('status', 'No status')
            problem = meta.get('problem', None)
            if problem is not None:
                title = problem.get('title', '')
                journal_status = ': '.join([journal_status, title])
            status.append(journal_status)

        counter = collections.Counter(status)
        msg = []
        for k, v in counter.most_common():
            msg.append(f'{v} tasks with status {k}')
        msg = '\n'.join(msg)
        self.logger.info('Report is:\n%s', msg)
        return msg

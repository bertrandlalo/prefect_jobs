import json
import pathlib
from typing import Dict, Optional
from urllib.parse import urlparse

from prefect.client import Secret

import iguazu
from iguazu.helpers.files import FileProxy, LocalFile, QuetzalFile
from iguazu.core.exceptions import PreconditionFailed
from iguazu.functions.typeform import fetch_responses


class FetchResponses(iguazu.Task):

    DEFAULT_BASE_URL = 'https://api.typeform.com'

    def __init__(self, *,
                 form_id: str,
                 base_url: str = DEFAULT_BASE_URL,
                 token_secret: str = 'TYPEFORM_TOKEN',
                 **kwargs):
        # import ipdb; ipdb.set_trace(context=21)
        super().__init__(**kwargs)
        self.form_id = form_id
        self.base_url = base_url
        self.token_secret = token_secret

    def run(self, **kwargs):
        self.logger.info('Requesting typeform responses of form %s at address %s',
                         self.form_id, self.base_url)

        token = str(Secret(self.token_secret).get())
        responses = fetch_responses(self.base_url, self.form_id, token)
        return responses

    def preconditions(self, **inputs):
        # import ipdb; ipdb.set_trace(context=21)
        if self.base_url is None:
            raise PreconditionFailed('base_url must not be None')
        if self.form_id is None:
            raise PreconditionFailed('form_id must not be None')

        url = urlparse(self.base_url)
        if url.scheme != 'https':
            raise PreconditionFailed('base_url must be a https address')


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
            response_id: str,
            workspace_id: Optional[int] = None,
            base_dir: Optional[str] = None) -> Optional[FileProxy]:

        output = self.default_outputs(workspace_id=workspace_id, base_dir=base_dir, response_id=response_id)
        self.logger.info('Saving response to %s', output)

        with open(output.filename, 'w') as f:
            json.dump(response, f, indent=2)

        return output

    def preconditions(self, **inputs):
        if self.form_id is None:
            raise PreconditionFailed('form_id must not be None')

        wid = inputs.get('workspace_id', None)
        base_dir = inputs.get('base_dir', None)
        response_id = inputs.get('response_id', None)
        if wid is None and base_dir is None:
            raise PreconditionFailed('Save task needs a workspace_id or base_dir')
        if wid is not None and base_dir is not None:
            raise PreconditionFailed('Save task workspace_id and base_dir parameters '
                                     'are mutually exclusive')
        if response_id is None:
            raise PreconditionFailed('Response identifier is a required input')

    def default_outputs(self, **inputs) -> Optional[FileProxy]:
        wid = inputs.get('workspace_id', None)
        base_dir = inputs.get('base_dir', None)
        response_id = inputs.get('response_id')
        file = None

        if wid is not None:
            file = QuetzalFile(workspace_id=wid)
            # TODO: QuetzalFile needs a way to create new files without parents

        elif base_dir is not None:
            filename = pathlib.Path(base_dir) / self.form_id / response_id / 'responses.json'
            file = LocalFile(str(filename), base_dir)

        return file



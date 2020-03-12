import click
from prefect import Parameter, unmapped
from prefect.engine.cache_validators import never_use
from prefect.tasks.control_flow import ifelse, merge
from prefect.tasks.core.operators import GetItem
from quetzal.client.cli import FamilyVersionListType

from iguazu.core.flows import PreparedFlow
from iguazu.core.handlers import logging_handler
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.common import LoadJSON, identity
from iguazu.tasks.metadata import AddDynamicMetadata, AddStaticMetadata
from iguazu.tasks.quetzal import CreateWorkspace, ScanWorkspace
from iguazu.tasks.typeform import (
    ExtractScores, FetchResponses, GetForm, GetUserHash, Save, DEFAULT_BASE_URL
)


class DownloadTypeform(PreparedFlow):
    """Download typeform responses"""

    REGISTRY_NAME = 'download_typeform'

    def _build(self, *,
               base_url=DEFAULT_BASE_URL,
               form_id=None,
               **kwargs):

        fetch = FetchResponses(
            base_url=base_url,
            form_id=form_id,
            force=True,   # this task should always run!
        )
        save = Save(form_id=form_id)
        get_token = GetItem(
            name='GetResponseID',
        )
        get_user_hash = GetUserHash()
        add_protocol_metadata = AddStaticMetadata(
            new_meta={
                'protocol': {
                    'name': 'vr-questionnaire',
                    'extra': {
                        'typeform_form_id': form_id,
                    },
                }
            }
        )
        add_user_metadata = AddDynamicMetadata(
            key=('omind', 'user_hash'),
        )

        with self:
            responses = fetch()
            response_id = get_token.map(task_result=responses, key=unmapped('token'))
            user_hash = get_user_hash.map(response=responses)
            files = save.map(response=responses,
                             response_id=response_id)
            add_protocol_metadata.map(file=files)
            add_user_metadata.map(file=files, value=user_hash)

    @staticmethod
    def click_options():
        return (
            click.option('--base-url', required=False, type=click.STRING, default=DEFAULT_BASE_URL,
                         help='Base URL for the typeform API.'),
            click.option('--form-id', required=False, type=click.STRING,
                         help='ID of the form (questionnaire) on typeform.'),
        )


class ExtractTypeformFeatures(PreparedFlow):

    REGISTRY_NAME = 'extract_typeform'
    DEFAULT_QUERY = None

    def _build(self, *,
               base_url=DEFAULT_BASE_URL,
               form_id=None,
               **kwargs):
        required_families = dict(
            iguazu=None,
            omi=None,
            standard=None,
            protocol=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families

        # When the query is set by kwargs, leave the query and dialect as they
        # come. Otherwise, set to the default defined just above
        if not kwargs.get('query', None):
            kwargs['query'] = self.DEFAULT_QUERY
            kwargs['dialect'] = 'postgresql_json'

        # First part of this flow: obtain a dataset of files
        dataset_flow = GenericDatasetFlow(**kwargs)

        json_files = dataset_flow.terminal_tasks().pop()
        self.update(dataset_flow)

        read_json = LoadJSON()
        read_form = GetForm(form_id=form_id, base_url=base_url)
        extract_scores = ExtractScores()

        with self:
            form = read_form()
            responses = read_json.map(file=json_files)
            scores = extract_scores.map(response=responses, form=unmapped(form))

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options() + (
            click.option('--base-url', required=False, type=click.STRING, default=DEFAULT_BASE_URL,
                         help='Base URL for the typeform API.'),
            click.option('--form-id', required=False, type=click.STRING,
                         help='ID of the form (questionnaire) on typeform.'),
        )


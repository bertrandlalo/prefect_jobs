import click
from prefect import unmapped
from prefect.tasks.core.operators import GetItem

from iguazu import  __version__
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.common import LoadJSON, SlackTask
from iguazu.tasks.metadata import AddDynamicMetadata, AddStaticMetadata
from iguazu.tasks.typeform import (
    ExtractScores, FetchResponses, GetForm, GetUserHash, Report, SaveResponse,
    DEFAULT_BASE_URL
)


class DownloadTypeform(PreparedFlow):
    """Download typeform responses to files"""

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
        save = SaveResponse(form_id=form_id)
        get_token = GetItem(
            name='GetResponseID',
        )
        get_user_hash = GetUserHash()
        add_protocol_metadata = AddStaticMetadata(
            new_meta={
                'protocol': {
                    'name': 'vr-questionnaire',
                    'extra': {
                        'form_id': form_id,
                    },
                }
            }
        )
        add_user_metadata = AddDynamicMetadata(
            key=('omind', 'user_hash'),
        )
        report = Report()
        notify = SlackTask(preamble='Download of typeform responses finished.\nTask report:')

        with self:
            responses = fetch()
            response_id = get_token.map(task_result=responses, key=unmapped('token'))
            user_hash = get_user_hash.map(response=responses)
            files = save.map(response=responses,
                             response_id=response_id)
            files_with_protocol = add_protocol_metadata.map(file=files)
            files_with_hash = add_user_metadata.map(file=files_with_protocol, value=user_hash)
            message = report(files=files_with_hash)
            notify(message=message)

    @staticmethod
    def click_options():
        return (
            click.option('--base-url', required=False, type=click.STRING, default=DEFAULT_BASE_URL,
                         help='Base URL for the typeform API.'),
            click.option('--form-id', required=False, type=click.STRING,
                         help='ID of the form (questionnaire) on typeform.'),
        )


class ExtractTypeformFeatures(PreparedFlow):
    """Extract all psychological features from typeform responses"""

    REGISTRY_NAME = 'features_typeform'
    DEFAULT_QUERY = f"""
SELECT base->>'id'         AS id,        -- id is the bare minimum needed for the query task to work
       base->>'filename'   AS filename,  -- this is just to help the human debugging this
       omind->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
       iguazu->>'version'  AS version    -- this is just to help the openmind human debugging this
FROM   metadata
WHERE  base->>'state' = 'READY'                -- No temporary files
AND    base->>'filename' LIKE '%.json'         -- Only JSON files
AND    protocol->>'name' = 'vr-questionnaire'  -- From the VR questionnaire (typeform) protocol
-- AND    protocol->>'extra'->'form_id' = '...'      -- Only from the VR questionnaire (TODO: think about this)
AND    COALESCE(iguazu->'flows'->'extract_typeform'->>'version', '') 
       < '{__version__}'                       -- That has not already been processed by this flow
ORDER BY id                                    -- always in the same order
"""

    def _build(self, *,
               base_url=DEFAULT_BASE_URL,
               form_id=None,
               **kwargs):
        required_families = dict(
            iguazu=None,
            omind=None,
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


import click
from prefect import unmapped
from prefect.tasks.core.operators import GetItem

from iguazu import __version__
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.common import LoadDataframe, LoadJSON, MergeDataframes, SlackTask
from iguazu.tasks.metadata import (
    AddDynamicMetadata, AddStaticMetadata, CreateFlowMetadata, UpdateFlowMetadata
)
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
            response_id = get_token.map(task_result=responses, key=unmapped('response_id'))
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
       base->>'filename'   AS filename   -- this is just to help the human debugging this
FROM   metadata
WHERE  base->>'state' = 'READY'                -- No temporary files
AND    base->>'filename' LIKE '%.json'         -- Only JSON files
AND    protocol->>'name' = 'vr-questionnaire'  -- From the VR questionnaire (typeform) protocol
-- AND    protocol->>'extra'->'form_id' = '...'      -- Only from the VR questionnaire (TODO: think about this)
AND    ( 
           iguazu->'flows'->'{REGISTRY_NAME}'->>'status' IS NULL         -- That has not already been succesfully processed by this flow
       OR  COALESCE(iguazu->'flows'->'{REGISTRY_NAME}'->>'version', '')  -- or if has been processed but by an outdated version
            < '{__version__}'
       )
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
            standard=None,
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

        create_flow_metadata = CreateFlowMetadata(flow_name=self.REGISTRY_NAME)
        read_json = LoadJSON()
        read_form = GetForm(form_id=form_id, base_url=base_url)
        extract_scores = ExtractScores(
            output_hdf5_key='/iguazu/features/typeform/subject',
        )
        # TODO: propagate metadata when the branch that has that task is merged
        # propagate_metadata = PropagateMetadata(propagate_families=['omind', 'protocol'])
        update_flow_metadata = UpdateFlowMetadata(flow_name=self.REGISTRY_NAME)

        with self:
            create_noresult = create_flow_metadata.map(parent=json_files)
            form = read_form()
            responses = read_json.map(file=json_files, upstream_tasks=[create_noresult])
            scores = extract_scores.map(parent=json_files, response=responses, form=unmapped(form))
            update_noresult = update_flow_metadata.map(parent=json_files, child=scores)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options() + (
            click.option('--base-url', required=False, type=click.STRING, default=DEFAULT_BASE_URL,
                         help='Base URL for the typeform API.'),
            click.option('--form-id', required=False, type=click.STRING,
                         help='ID of the form (questionnaire) on typeform.'),
        )


class SummarizeTypeformFlow(PreparedFlow):
    """ Collect all typeform features in a single CSV file """

    REGISTRY_NAME = 'summarize_typeform'
    DEFAULT_QUERY = f"""
SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
       base->>'filename' AS filename  -- this is just to help the human debugging this
FROM metadata
WHERE  base->>'state' = 'READY'                -- No temporary files
AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
AND    standard->'features' ? '/iguazu/features/typeform/subject' -- containing the typeform features
AND    iguazu->>'version' = '{__version__}'    -- Select only files generated with last version 
                                               -- (avoids ending with corrupted local file)
ORDER BY id -- always in the same order
"""

    def _build(self, **kwargs):
        required_families = dict(
            iguazu=None,
            omind=None,
            protocol=None,
            standard=None,
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

        features_files = dataset_flow.terminal_tasks().pop()
        self.update(dataset_flow)

        read_features = LoadDataframe(
            key='/iguazu/features/typeform/subject',
        )
        merge_features = MergeDataframes(
            filename='typeform_summary.csv',
            path='datasets',
        )
        notify = SlackTask(message='Typeform feature summarization finished!')

        with self:
            feature_dataframes = read_features.map(file=features_files)
            merged_dataframe = merge_features(parents=features_files, dataframes=feature_dataframes)
            # Send slack notification
            notify(upstream_tasks=[merged_dataframe])

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()

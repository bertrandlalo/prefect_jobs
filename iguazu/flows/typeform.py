import click
from prefect import Parameter, unmapped
from prefect.engine.cache_validators import never_use
from prefect.tasks.control_flow import ifelse, merge
from prefect.tasks.core.operators import GetItem
from quetzal.client.cli import FamilyVersionListType

from iguazu.core.flows import PreparedFlow
from iguazu.tasks.common import AddSourceMetadata, identity
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, ScanWorkspace
from iguazu.tasks.typeform import FetchResponses, GetUserHash, Save, DEFAULT_BASE_URL


class ExtractTypeform(PreparedFlow):
    """Download typeform responses"""

    REGISTRY_NAME = 'download_typeform'

    def _build(self, *,
               base_url=DEFAULT_BASE_URL,
               form_id=None,
               data_sink='local',
               # data_target='local',
               base_dir=None,
               workspace_name=None,
               families=None,
               **kwargs):

        required_families = dict(
            iguazu=None,
            protocol=None,
            omi=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])

        fetch = FetchResponses(base_url=base_url, form_id=form_id)
        save = Save(form_id=form_id)
        create_or_retrieve = CreateWorkspace(
            # Iguazu task constructor arguments
            exist_ok=True,
            families=families,
            workspace_name=workspace_name,
            # Prefect task arguments
            state_handlers=[logging_handler],
            cache_validator=never_use,
        )
        scan = ScanWorkspace(
            # Iguazu task constructor arguments
            # ... None ...
            # Prefect task arguments
            name='ScanWorkspace',  # Needs to set name otherwise it will be named _WorkspaceOperation
            state_handlers=[logging_handler],
            cache_validator=never_use,
        )
        get_token = GetItem()
        get_user_hash = GetUserHash()
        add_metadata = AddSourceMetadata(
            new_meta={
                'protocol': {
                    'name': 'vr-questionnaire',
                    'program': 'typeform',
                    'typeform-form': form_id,
                }
            }
        )

        with self:
            # quetzal branch
            wid = create_or_retrieve()
            wid_ready = scan(wid)
            # local branch
            local_dir = Parameter('local_dir', default=base_dir, required=False)
            local_dir = identity(local_dir)
            wid_none = identity(Parameter('wid_none', default=None, required=False))
            dir_none = identity(Parameter('dir_none', default=None, required=False))
            # merge quetzal and local branch
            # sink = Parameter('sink', default=data_sink, required=False)
            ifelse(data_sink == 'quetzal', wid, wid_none)
            merged_wid = merge(wid_ready, wid_none)
            ifelse(data_sink == 'local', local_dir, dir_none)
            merged_dir = merge(local_dir, dir_none)

            # data retrieval branch and merge
            user_hash_key = identity(Parameter('user_hash_key', default=[('omi', 'user_hash')], required=False))
            responses = fetch()
            response_id = get_token.map(task_result=responses, key=unmapped('token'))
            user_hash = get_user_hash.map(response=responses)
            files = save.map(response=responses,
                             response_id=response_id,
                             workspace_id=unmapped(merged_wid),
                             base_dir=unmapped(merged_dir))
            add_metadata.map(file=files,
                             extra_keys=unmapped(user_hash_key),
                             extra_values=user_hash)



    @staticmethod
    def click_options():
        return (
            click.option('--base-url', required=False, type=click.STRING, default=DEFAULT_BASE_URL,
                         help='Base URL for the typeform API.'),
            click.option('--form-id', required=False, type=click.STRING,
                         help='ID of the form (questionnaire) on typeform.'),
            click.option('--data-sink', type=click.Choice(['local', 'quetzal']), default='local',
                         help='Sink of data to choose for this flow.'),
            click.option('--base-dir', required=False,
                         type=click.Path(dir_okay=True, file_okay=False),
                         help='Local data directory.'),
            click.option('--workspace-name', required=False, type=click.STRING,
                         help='Name of the Quetzal workspace where data will be saved.'),
            click.option('--families', type=FamilyVersionListType(),
                         metavar='NAME:VERSION[,...]', required=False,
                         help='Comma-separated family NAMEs and VERSIONs to declare when '
                              'creating a new Quetzal workspace, or to ensure that they '
                              'are needed when an existing Quetzal workspace is retrieved. '
                              'For example: "--families base:latest,xdf:10" means that '
                              'the workspace should use the most recent version of the '
                              '"base" family, and the version 10 of the "xdf" family.'),
        )

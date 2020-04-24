import copy
from typing import Any, Dict, List, Optional, Tuple

import prefect

import iguazu
from iguazu import __version__, FileAdapter
from iguazu.utils import deep_update


class CreateFlowMetadata(iguazu.Task):
    """ Create flow key with current registry name in family iguazu -> flows """

    def __init__(self, *, flow_name, **kwargs):
        super().__init__(**kwargs)
        self.flow_name = flow_name

    def run(self, *, parent: FileAdapter) -> None:
        journal_family = self.meta.metadata_journal_family
        new_meta = {
            journal_family: {
                'flows': {
                    self.flow_name: {
                        'status': None,
                        'version': __version__,
                    }
                }
            }
        }
        deep_update(parent.metadata, new_meta)
        parent.upload_metadata()


class UpdateFlowMetadata(iguazu.Task):
    """ Update status of current flow in metadata"""

    def __init__(self, *, flow_name, **kwargs):
        super().__init__(**kwargs)
        self.flow_name = flow_name

    def run(self, *, parent: FileAdapter, child: FileAdapter) -> None:
        journal_family = self.meta.metadata_journal_family
        new_meta = {
            journal_family: {
                'flows': {
                    self.flow_name: {
                        'status': child.metadata[journal_family]['status'],  # todo get status from child
                        'version': __version__,
                    }
                }
            }
        }
        deep_update(parent.metadata, new_meta)
        parent.upload_metadata()


class AddStaticMetadata(prefect.Task):
    """Updates the metadata of a file from a static template

    Use this task when you know the metadata changes before building the flow
    and the metadata values do not depend on a dynamic value (from the flow
    execution).
    """

    def __init__(self, *, new_meta: Dict, **kwargs):
        super().__init__(**kwargs)
        self.new_meta = new_meta

    def run(self, *, file: FileAdapter) -> FileAdapter:
        new_meta = copy.deepcopy(self.new_meta)
        deep_update(file.metadata, new_meta)
        file.upload_metadata()
        return file


class AddDynamicMetadata(prefect.Task):
    """Updates the metadata of a file from a static key but dynamic value

     Use this task when you know the key of the metadata to change before
     building the flow, but the value comes from a dynamic value only known
     when the flow is executed.
     """

    def __init__(self, *, key: Tuple[str, ...], **kwargs):
        super().__init__(**kwargs)
        self.key_tuple = key

    def run(self, *,
            file: FileAdapter,
            value: Any) -> FileAdapter:

        current_level = file.metadata
        for k in self.key_tuple[:-1]:
            current_level.setdefault(k, {})
            current_level = current_level[k]

        last_key = self.key_tuple[-1]
        current_level[last_key] = value
        file.upload_metadata()
        return file


class PropagateMetadata(prefect.Task):

    def __init__(self, *, propagate_families: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.propagate_families = propagate_families

    def run(self, *, parent: FileAdapter, child: FileAdapter) -> FileAdapter:
        # Propagate metadata
        parent_metadata = copy.deepcopy(parent.metadata)
        for k in self.propagate_families:
            parent_meta = parent_metadata.get(k, {})
            parent_meta.pop('id', None)
            deep_update(child.metadata, {k: parent_meta})
        # upload metadata
        child.upload_metadata()
        return child


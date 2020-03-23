import copy
import logging
from typing import Dict, NoReturn, Optional, List

import prefect

from iguazu import __version__, FileAdapter
from iguazu.utils import deep_update

logger = logging.getLogger(__name__)


class CreateFlowMetadata(prefect.Task):
    """ Create flow key with current registry name in family iguazu -> flows """

    def __init__(self, *, flow_name, **kwargs):
        super().__init__(**kwargs)
        self.flow_name = flow_name

    def run(self, *, parent: FileAdapter) -> NoReturn:
        new_meta = {
            'iguazu': {
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


class UpdateFlowMetadata(prefect.Task):
    """ Update status of current flow in metadata"""

    def __init__(self, *, flow_name, **kwargs):
        super().__init__(**kwargs)
        self.flow_name = flow_name

    def run(self, *, parent: FileAdapter, child: FileAdapter) -> NoReturn:
        new_meta = {
            'iguazu': {
                'flows': {
                    self.flow_name: {
                        'status': child.metadata['iguazu']['status'],  # todo get status from child
                        'version': __version__,
                    }
                }
            }
        }
        deep_update(parent.metadata, new_meta)
        parent.upload_metadata()


class AddSourceMetadata(prefect.Task):

    def __init__(self, *, new_meta: Dict, **kwargs):
        super().__init__(**kwargs)
        self.new_meta = new_meta

    def run(self, *, file: FileAdapter) -> NoReturn:
        new_meta = copy.deepcopy(self.new_meta)
        deep_update(file.metadata, new_meta)
        file.upload_metadata()


class PropagateMetadata(prefect.Task):

    def __init__(self, *, propagate_families: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.propagate_families = propagate_families

    def run(self, *, parent: FileAdapter, child: FileAdapter) -> FileAdapter:
        # Propagate metadata
        deep_update(child.metadata, {propagate_family: parent.metadata.get(propagate_family, {})
                                     for propagate_family in self.propagate_families})
        # upload metadata
        child.upload_metadata()
        return child

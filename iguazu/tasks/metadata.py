import copy
import logging
from typing import Dict, NoReturn

import prefect

from iguazu import __version__ as version
from iguazu.core.files import FileAdapter, _deep_update

logger = logging.getLogger(__name__)


class CreateFlowMetadata(prefect.Task):
    """ Create flow key with current registry name in family iguazu -> flows """

    def __init__(self, *, flow_name, **kwargs):
        super().__init__(**kwargs)
        self.flow_name = flow_name

    def run(self, *, parent: FileAdapter) -> NoReturn:
        new_meta = {'iguazu': {
            'flows':
                {self.flow_name:
                     {'status': None,
                      'version': version}}
        }
        }
        _deep_update(parent.metadata, new_meta)
        # TODO: for quetzal, we are going to need a .upload_metadata method
        #       so we don't download the file for nothing
        parent.upload()


class UpdateFlowMetadata(prefect.Task):
    """ Update status of current flow in metadata"""

    def __init__(self, *, flow_name, **kwargs):
        super().__init__(**kwargs)
        self.flow_name = flow_name

    def run(self, *, parent: FileAdapter, child: FileAdapter) -> NoReturn:
        new_meta = {'iguazu': {
            'flows':
                {self.flow_name:
                     {'status': child.metadata['iguazu']['status'],  # todo get status from child
                      'version': version}}
        }
        }
        _deep_update(parent.metadata, new_meta)
        # TODO: for quetzal, we are going to need a .upload_metadata method
        #       so we don't download the file for nothing
        parent.upload()


class AddSourceMetadata(prefect.Task):

    def __init__(self, *, new_meta: Dict, **kwargs):
        super().__init__(**kwargs)
        self.new_meta = new_meta

    def run(self, *, file: FileAdapter) -> NoReturn:
        new_meta = copy.deepcopy(self.new_meta)
        _deep_update(file.metadata, new_meta)
        # TODO: for quetzal, we are going to need a .upload_metadata method
        #       so we don't download the file for nothing
        file.upload()

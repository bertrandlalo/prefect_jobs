import abc
import collections
import logging
import pathlib
from typing import Any, Dict

from prefect import context
from quetzal.client import helpers
from quetzal.client.utils import get_data_dir

logger = logging.getLogger(__name__)


class FileProxy(abc.ABC):

    @property
    @abc.abstractmethod
    def file(self) -> pathlib.Path:
        pass

    @property
    @abc.abstractmethod
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        pass


class QuetzalFile(FileProxy):

    def __init__(self, metadata, workspace_id=None, id_key='id', **kwargs):
        if id_key not in metadata:
            raise ValueError('Cannot create Quetzal file proxy without id')
        super().__init__()

        self._file_id = metadata[id_key]
        self._meta = collections.defaultdict(dict)
        self._meta.update(metadata or {})
        self._workspace_id = workspace_id

        self._local_file = None
        self._client_kwargs = kwargs or {}

    @property
    def file(self) -> pathlib.Path:
        if self._local_file is None:
            download_dir = get_data_dir()
            logger.debug('Downloading %s -> %s', self._file_id, download_dir)
            filename = helpers.file.download(self.client,
                                             self._file_id,
                                             self._workspace_id,
                                             output_dir=download_dir)
            self._local_file = pathlib.Path(filename)
            logger.debug('Downloaded %s -> %s', self._file_id, self._local_file)
        return self._local_file

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        return self._meta

    @property
    def client(self):
        if 'quetzal_client' in context:
            return context.quetzal_client
        return helpers.get_client(**self._client_kwargs)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_local_file']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._local_file = None


class LocalFile(FileProxy):

    def __init__(self, file, metadata=None):
        super().__init__()
        self._file = pathlib.Path(file)
        self._meta = collections.defaultdict(dict)
        self._meta.update(metadata or {})

    @property
    def file(self) -> pathlib.Path:
        return self._file

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        return self._meta

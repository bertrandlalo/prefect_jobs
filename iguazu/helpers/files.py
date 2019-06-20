import abc
import collections
import copy
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

    @abc.abstractmethod
    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=False) -> 'FileProxy':
        # TODO: change extension
        pass

    @abc.abstractmethod
    def upload(self):
        pass


class QuetzalFile(FileProxy):

    def __init__(self, file_id=None, workspace_id=None, **client_kwargs):
        # if id_key not in metadata:
        #     raise ValueError('Cannot create Quetzal file proxy without id')
        super().__init__()
        self._file_id = file_id
        self._metadata = collections.defaultdict(dict)
        self._wid = workspace_id
        self._local_path = None
        self._client_kwargs = client_kwargs or {}
        self._temporary = False

    @property
    def file(self) -> pathlib.Path:
        if self._local_path is None:
            download_dir = get_data_dir()
            logger.debug('Downloading %s -> %s', self._file_id, download_dir)
            filename = helpers.file.download(self.client,
                                             self._file_id,
                                             self._wid,
                                             output_dir=download_dir)
            self._local_path = pathlib.Path(filename)
            logger.debug('Downloaded %s -> %s', self._file_id, self._local_path)
        return self._local_path

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        if self._file_id is not None and not self._metadata:
            quetzal_metadata = helpers.file.metadata(self.client, self._file_id, self._wid)
            self._metadata.update(quetzal_metadata)
        return self._metadata

    @property
    def client(self):
        # if 'quetzal_client' in context:
        #     return context.quetzal_client
        if 'quetzal_client' in context:
            return helpers.get_client(**context.quetzal_client)
        return helpers.get_client(**self._client_kwargs)

    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=False) -> 'QuetzalFile':
        # TODO: define what metadata gets inherited!
        # TODO: what if file already exists in quetzal? How do we check this?
        if 'temp_dir' not in context or context.temp_dir is None:
            raise RuntimeError('Cannot create new file without a "temp_dir" on '
                               'the prefect context')
        temp_dir = pathlib.Path(context.temp_dir)

        # Create a new file with the help of pathlib
        # First, the path
        base_metadata = self.metadata['base']
        if path is None:
            new = temp_dir / pathlib.PosixPath(base_metadata['path'])
        else:
            new = temp_dir / pathlib.Path(path)
        # Then, the filename
        if filename is None:
            new = new / base_metadata['filename']
        else:
            new = new / filename
        # Adjust the suffix and extension
        suffix = suffix or ''
        extension = extension or new.suffix
        new = new.with_name(new.stem + suffix + extension)

        # Create new child proxy class and propagate metadata
        child = QuetzalFile(file_id=None,
                            workspace_id=self._wid,
                            **self._client_kwargs)
        child._metadata = copy.deepcopy(self._metadata)
        child._metadata.pop('base', None)
        child._metadata['base']['filename'] = new.name
        child._metadata['base']['path'] = str(new.relative_to(temp_dir).parent)
        # unset all id columns
        for family in child._metadata:
            child._metadata[family]['id'] = None
        # link child to parent
        child._metadata['iguazu']['parents'] = base_metadata['id']

        child._local_path = new
        child._temporary = temporary
        return child

    def upload(self):
        logger.info('Uploading %s to Quetzal', self._local_path)
        if self._local_path is None or not self._local_path.exists():
            raise RuntimeError('Cannot upload if file does not exist')
        with open(self._local_path, 'rb') as fd:
            details = helpers.workspace.upload(self.client, self._wid, fd,
                                               path=self.metadata['base']['path'],
                                               temporary=self._temporary)
        self._file_id = details.id
        metadata = copy.deepcopy(self.metadata)
        for family in metadata:
            if 'id' in metadata[family]:
                metadata[family].pop('id')
        helpers.workspace.update_metadata(self.client, self._wid, self._file_id, metadata)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_local_path']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._local_path = None

    def __repr__(self):
        base_metadata = self.metadata.get('base', {})
        fid = base_metadata.get('id', 'unindentified')
        filename = base_metadata.get('filename', 'unnamed')
        return f'QuetzalFile<id={fid}, filename={filename}>'


class LocalFile(FileProxy):

    def __init__(self, file):
        super().__init__()
        self._file = pathlib.Path(file)
        self._metadata = collections.defaultdict(dict)

    @property
    def file(self) -> pathlib.Path:
        return self._file

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self._metadata:
            self._metadata['base']['filename'] = str(self._file.name)
            self._metadata['base']['path'] = str(self._file.parent)
        return self._metadata

    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=False) -> 'LocalFile':
        if 'temp_dir' not in context or context.temp_dir is None:
            raise RuntimeError('Cannot create new file without a "temp_dir" on '
                               'the prefect context')
        temp_dir = pathlib.Path(context.temp_dir)

        # Create a new file with the help of pathlib
        # First, the path
        base_metadata = self.metadata['base']
        if path is None:
            new = temp_dir / pathlib.PosixPath(base_metadata['path'])
        else:
            new = temp_dir / pathlib.Path(path)
        # Then, the filename
        if filename is None:
            new = new / base_metadata['filename']
        else:
            new = new / filename
        # Adjust the suffix and extension
        suffix = suffix or ''
        extension = extension or new.suffix
        new = new.with_name(new.stem + suffix + extension)

        # Create new child proxy class and propagate metadata
        child = LocalFile(new)
        return child

    def upload(self):
        # Upload on local file does nothing
        pass

    def __repr__(self):
        base_metadata = self.metadata.get('base', {})
        filename = base_metadata.get('filename', 'unnamed')
        return f'LocalFile<filename={filename}>'


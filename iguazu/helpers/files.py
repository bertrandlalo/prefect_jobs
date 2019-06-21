import abc
import collections
import copy
import json
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
    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=True) -> 'FileProxy':
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
        # TODO: reuse previous client if possible...
        #       but needs some intelligence with respect to context
        if 'quetzal_client' in context:
            return helpers.get_client(**context.quetzal_client)
        return helpers.get_client(**self._client_kwargs)

    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=True) -> 'QuetzalFile':
        # TODO: define what metadata gets inherited!
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

        # Verify if there already a child with the same name, path and parent
        existing_meta = self._retrieve_child_meta(str(new.relative_to(temp_dir).parent), new.name)
        if existing_meta:
            child = QuetzalFile(file_id=existing_meta['base']['id'],
                                workspace_id=self._wid,
                                **self._client_kwargs)
            child._metadata = existing_meta
            # Propagate parent metadata (drop base metadata, drop all ids)
            parent_metadata = copy.deepcopy(self._metadata)
            for family in parent_metadata:
                parent_metadata[family].pop('id', None)
            parent_metadata.pop('base', None)
            if 'iguazu' in parent_metadata:
                parent_metadata['iguazu'].pop('parents', None)
            child._metadata = _deep_update(child._metadata, parent_metadata)
            return child

        # Create new child proxy class and propagate metadata
        child = QuetzalFile(file_id=None,
                            workspace_id=self._wid,
                            **self._client_kwargs)
        child._metadata = copy.deepcopy(self._metadata)
        if not isinstance(child._metadata, collections.defaultdict):
            tmp = collections.defaultdict(dict)
            tmp.update(child._metadata)
            child._metadata = tmp
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

    def _retrieve_child_meta(self, path, filename):
        logger.info('Retrieving possible child')
        parent_id = self._file_id
        candidates = helpers.file.find(self.client, wid=self._wid, path=path, filename=filename)
        logger.info('File by name and path gave %d candidates', len(candidates))
        for file_detail in sorted(candidates, key=lambda d: d.date, reverse=True):
            meta = helpers.file.metadata(self.client, file_detail.id, wid=self._wid)
            parent = meta.get('iguazu', {}).get('parents', None)
            if parent == parent_id:
                logger.info('Found a match with same parent %s', meta['base'])
                return meta
        logger.info('No candidate matches')
        return None

    def upload(self):
        logger.info('Uploading %s to Quetzal', self._local_path)
        if self._file_id is not None:
            logger.info('File already has an id, no need to upload')
        elif self._local_path is None or not self._local_path.exists():
            raise RuntimeError('Cannot upload if file does not exist')
        else:
            with open(self._local_path, 'rb') as fd:
                details = helpers.workspace.upload(self.client, self._wid, fd,
                                                   path=self.metadata['base']['path'],
                                                   temporary=self._temporary)
            self._file_id = details.id

        self._upload_metadata()

    def _upload_metadata(self):
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

    def __init__(self, file, base_dir):
        super().__init__()
        self._file = pathlib.Path(file)
        self._base_dir = pathlib.Path(base_dir)
        self._relative_dir = self._file.relative_to(base_dir).parent
        self._meta_file = self._file.with_name(self._file.name + ".json")
        if self._meta_file.exists():
            with open(self._meta_file) as json_file:
                self._metadata = json.load(json_file)
        else:
            self._metadata = collections.defaultdict(dict) # type: Dict[str, Dict[str, Any]]

    @property
    def file(self) -> pathlib.Path:
        self._file.parent.mkdir(parents=True, exist_ok=True)
        return self._file

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self._metadata:  # TODO: if json is present but not metadata, read it from there
            self._metadata['base']['filename'] = str(self._file.name)
            self._metadata['base']['path'] = str(self._file.parent)
        return self._metadata

    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=True) -> 'LocalFile':
        """ Creates a child FileProxy that inherits from its parent's metadata.

        Parameters
        ----------
        filename: name of the FileProxy to create. If None, the a suffix is added to the parent's FileProxy
        and the direction is given in the context by 'temp_dir'.
        path: path relative to temp_dir where the child FileProxy is created (eg. "/preprocessed/galvanic") . If None, the relative path is the same
        as it's parent relative to base_dir.
        suffix: suffix to add at the end of the filename (eg. "_clean"). If None, nothing is added.
        extension: extension of the child FileProxy (eg. "hdf5", "csv", "png", ... ) . If None, the extension is the same as it's parent.
        temporary: not implemented yet.

        Returns
        -------

        """
        if 'temp_dir' not in context or context.temp_dir is None:
            raise RuntimeError('Cannot create new file without a "temp_dir" on '
                               'the prefect context')
        if temporary:
            file_dir = pathlib.Path(context.temp_dir)
        else:
            file_dir = pathlib.Path(context.output_dir)
        # Create a new file with the help of pathlib
        # First, the path
        base_metadata = self.metadata['base']
        if path is None:
            new = file_dir / self._relative_dir
        else:
            new = file_dir / pathlib.Path(path)
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
        child = LocalFile(new, base_dir=file_dir)
        return child

    def upload(self):
        # Upload on local file does nothing
        with open(self._meta_file, 'w') as outfile:
            json.dump(self.metadata, outfile)

    def __repr__(self):
        base_metadata = self.metadata.get('base', {})
        filename = base_metadata.get('filename', 'unnamed')
        return f'LocalFile<filename={filename}>'


def _deep_update(dest, src):
    for k, v in src.items():
        if isinstance(v, collections.Mapping):
            dest[k] = _deep_update(dest.get(k, {}), v)
        else:
            dest[k] = v
    return dest

import collections
import json
import logging
import pathlib
from typing import Dict, Any, Optional

from prefect import context
from quetzal.client.utils import get_data_dir, get_readable_info

from iguazu.core.files import FileAdapter, LocalURL
from iguazu.utils import mapping_issubset

# Notice the quetzal import just above: Even if we are on local file,
# we want to have the same local directory to "download" files

logger = logging.getLogger(__name__)


class LocalFile(FileAdapter):
    """File adapter implementation that uses local files

    This class is provided for local development of Iguazu tasks and flows.
    Local files use a :py:class:`pathlib.Path` as its underlying data backend,
    with a directory that may be different for temporary and non-temporary
    files.

    To track metadata, local files use a JSON file with the same name as its
    associated data file. For example a file named ``dir/data_20090302.hdf5``
    will have its associated metadata at ``dir/data_20090302.hdf5.json``.

    """

    def __init__(self, *,
                 filename: str,
                 path: Optional[str] = None,
                 temporary: bool = False,
                 metadata: Optional[Dict] = None,
                 root: Optional[str] = None,
                 **kwargs):
        # Some sanity checks
        if temporary:
            if 'temp_url' not in context:
                logger.warning('Creating a temporary file, but no temp_url found in '
                               'context. Are you creating a file outside a prefect '
                               'task or flow?')
            if not isinstance(context.temp_url, LocalURL):
                logger.warning('Creating a temporary file, but temp_url is not a '
                               'Local URL like "file://...", this seems wrong')
        else:
            if 'output_url' not in context:
                logger.warning('Creating a non-temporary file, but no output_url found in '
                               'context. Are you creating a file outside a prefect '
                               'task or flow?')
            if not isinstance(context.output_url, LocalURL):
                logger.warning('Creating a non-temporary file, but output_url is not a '
                               'Local URL like "file://...", this seems wrong')

        super().__init__(filename=filename, path=path, temporary=temporary, **kwargs)
        self._temporary = temporary
        self._file_id = None
        self._metadata = collections.defaultdict(dict, metadata or {})
        self._root = root
        if self._root is None:
            if temporary:
                if context.temp_url.backend == 'local':
                    self._root = context.temp_url.path
                else:  # quetzal
                    # Note: Even if we are on local file, we want to have the same
                    # local directory as QuetzalFile to "download" files
                    self._root = get_data_dir()
            else:
                if context.output_url.backend == 'local':
                    self._root = context.output_url.path
                else:  # quetzal
                    # Note: Even if we are on local file, we want to have the same
                    # local directory as QuetzalFile to "download" files
                    self._root = get_data_dir()

        path = path or ''
        self._local_path = pathlib.Path(self._root) / path / filename
        self._local_meta = self._local_path.with_name(self._local_path.name + '.json')

    # def __oldinit__(self, file, base_dir):
    #     super().__init__()
    #     self._file = pathlib.Path(file)
    #     self._file_id = str(self._file)
    #     self._base_dir = pathlib.Path(base_dir)
    #     self._relative_dir = self._file.relative_to(base_dir).parent
    #     self._meta_file = self._file.with_name(self._file.name + ".json")
    #     if self._meta_file.exists():
    #         with open(self._meta_file) as json_file:
    #             self._metadata = json.load(json_file)
    #     else:
    #         self._metadata = collections.defaultdict(dict)  # type: Dict[str, Dict[str, Any]]

    @staticmethod
    def find(*, filename, path, metadata, temporary) -> Optional['LocalFile']:
        logger.debug('Search local file with filename %s path %s, metadata %s '
                     'and temporary is %s',
                     filename, path, metadata, temporary)
        path = path or ''
        if temporary:
            root = context.temp_url.path
        else:
            root = context.output_url.path
        # root = context.temp_dir if temporary else get_data_dir()  # todo: get_data_dir is quetzal!
        candidate = pathlib.Path(root) / path / filename
        file_id = str(candidate.relative_to(root))
        if candidate.exists():
            logger.debug('Found one candidate file at %s', str(candidate.resolve()))
            # instance = LocalFile(filename=filename, path=path, temporary=temporary
            instance = LocalFile.retrieve(file_id=file_id, temporary=temporary)
            meta = instance.metadata
            if not mapping_issubset(metadata, meta):
                logger.debug('Candidate does not match requested metadata, discarding')
                return None

            logger.debug('Candidate matches state, metadata, file and path: %s',
                         instance)
            return instance

        logger.debug('No matches found')
        return None

    @staticmethod
    def retrieve(*, file_id, temporary=False, root=None) -> Optional['LocalFile']:
        tmp = pathlib.Path(file_id)
        path = str(tmp.parent)
        if path == '.':
            path = ''
        # Create a bare Local file...
        instance = LocalFile(filename=tmp.name, path=path, temporary=temporary, root=root)
        # ... and then complete its file_id
        instance._file_id = file_id

        # ...finally, just check that the instance _local_path is not pointing
        # to old data to avoid confusion
        if instance._local_path.exists():
            with instance._local_path.open('rb') as fd:
                local_is_valid = instance.checksum(fd)
            if not local_is_valid:
                logger.debug('File %s already exists locally in %s,'
                             'but its size and checksum differ from its accompanying '
                             'metadata file. Erasing local file...', file_id, instance.file)
                instance.delete()
        return instance

    @property
    def file(self) -> pathlib.Path:
        if not self._local_path.exists():
            self.download_data()
        return self._local_path
        # """ Reference to the local file as a :py:class:`pathlib.Path`
        #
        # Read the parent :py:attr:`~LocalFile.file` property documentation for
        # more details on the general behavior for this property.
        #
        # Since underlying storage of a :py:class:`LocalFile` is a regular file,
        # using this property does not incur in any download operation.
        # However, it will create the directory structure of the file if it
        # does not exist before. This is done to simplify any write operation on
        # the file, which would otherwise require the user to add a lot of
        # boilerplate code to verify and create the directory structure.
        #
        # """
        # self._file.parent.mkdir(parents=True, exist_ok=True)
        # return self._file

    @property
    def basename(self) -> str:
        return self._local_path.name

    @property
    def dirname(self) -> str:
        return str(self._local_path.relative_to(self._root).parent)

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self._metadata:
            self.download_metadata()
        return self._metadata

    @property
    def id(self) -> Optional[str]:
        if self._file_id is None:
            return None
        return str(self._file_id)

    @property
    def empty(self):
        if not self._local_path.exists():
            return 0
        else:
            return self.file.stat().st_size == 0

    # @property
    # def metadata(self) -> Dict[str, Dict[str, Any]]:
    #     if not self._metadata:  # TODO: if json is present but not metadata, read it from there
    #         self._metadata['base']['filename'] = str(self._file.name)
    #         self._metadata['base']['path'] = str(self._file.parent)
    #         self._metadata['base']['id'] = self._file_id
    #
    #     return self._metadata

    # @property
    # def id(self) -> Optional[str]:
    #     return str(self._file)

    # def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=True) -> 'LocalFile':
    #     """ Creates a child FileAdapter that inherits from its parent's metadata.
    #
    #     Parameters
    #     ----------
    #     filename: name of the FileAdapter to create. If None, the a suffix is added to the parent's FileAdapter
    #     and the direction is given in the context by 'temp_dir'.
    #     path: path relative to temp_dir where the child FileAdapter is created (eg. "/preprocessed/galvanic") . If None, the relative path is the same
    #     as it's parent relative to base_dir.
    #     suffix: suffix to add at the end of the filename (eg. "_clean"). If None, nothing is added.
    #     extension: extension of the child FileAdapter (eg. "hdf5", "csv", "png", ... ) . If None, the extension is the same as it's parent.
    #     temporary: not implemented yet.
    #
    #     Returns
    #     -------
    #
    #     """
    #     if 'temp_dir' not in context or context.temp_dir is None:
    #         raise RuntimeError('Cannot create new file without a "temp_dir" on '
    #                            'the prefect context')
    #     if temporary:
    #         file_dir = pathlib.Path(context.temp_dir)
    #     else:
    #         file_dir = pathlib.Path(context.output_dir)
    #     # Create a new file with the help of pathlib
    #     # First, the path
    #     base_metadata = self.metadata['base']
    #     if path is None:
    #         new = file_dir / self._relative_dir
    #     else:
    #         new = file_dir / pathlib.Path(path)
    #     # Then, the filename
    #     if filename is None:
    #         new = new / base_metadata['filename']
    #     else:
    #         new = new / filename
    #     # Adjust the suffix and extension
    #     suffix = suffix or ''
    #     extension = extension or new.suffix
    #     new = new.with_name(new.stem + suffix + extension)
    #     child_exists = False
    #     if new.exists():
    #         child_exists = True
    #     # Retrieve or create child
    #     child = LocalFile(new, base_dir=file_dir)
    #     child._local_path = new
    #     child._temporary = temporary
    #
    #     # If child has just been created, propagate metadata
    #     if not child_exists:
    #         child = LocalFile(new, base_dir=file_dir)
    #         child._local_path = new
    #         child._temporary = temporary
    #         # TODO: think: perhaps remove child metadata propagation
    #         child._metadata = copy.deepcopy(self._metadata)
    #         if not isinstance(child._metadata, collections.defaultdict):
    #             tmp = collections.defaultdict(dict)
    #             tmp.update(child._metadata)
    #             child._metadata = tmp
    #         child._metadata.pop('base', None)
    #         child._metadata['base']['filename'] = new.name
    #         child._metadata['base']['path'] = str(new.relative_to(file_dir).parent)
    #         child._metadata['base']['id'] = child._file_id
    #         # # NEW! and TODO: we must remove the iguazu family!
    #         # Response: no, the iguazu.Task takes care of setting the iguazu family
    #         #
    #         # child._metadata.pop('iguazu', None)
    #         # if 'iguazu' in child._metadata:
    #         #     del child._metadata['iguazu']
    #         #child._metadata['iguazu']['parents'] = [base_metadata['id']]
    #         # # unset iguazu state
    #         # child._metadata['iguazu'].pop('state', None)
    #
    #     return child

    def upload_data(self):
        if self._file_id is not None:
            logger.debug('File already has an id, no need to upload')
        elif not self._local_path.exists():
            logger.error('Something is wrong: uploading a file that does not exist')
            raise RuntimeError('Cannot upload if file does not exist')
        else:
            self._file_id = str(self._local_path.relative_to(self._root))
        self._metadata.setdefault('base', {})
        self._metadata['base']['id'] = self._file_id

    def upload_metadata(self):
        # Upload on local file dumps the meta in a json
        meta = self.metadata
        with self._local_meta.open('w') as outfile:
            json.dump(meta, outfile, indent=2, sort_keys=True)
        # unset the metadata so that next time it is refreshed
        self._metadata.clear()

    def delete(self):
        logger.debug('Deleting local file %s', self)
        # TODO: when we update to Python 3.8, use unlink(missing_ok=True)
        #       instead of these if statements.
        if self._local_path.exists():
            self._local_path.unlink()
        if self._local_meta.exists():
            self._local_meta.unlink()
        if self._file_id is not None:
            self._file_id = None
        self._metadata.clear()

    def clean(self):
        logger.debug('Clean on local file is a no-op')

    def download_data(self):
        if self._file_id is not None and not self._local_path.exists():
            # File exists in quetzal
            logger.debug('Downloading local file %s -> %s is no-op because it is a'
                         'LocalFile instace', self._file_id, self._local_path)
        else:
            # File does not exist yet, it is probably a new file
            # ... here, just create the directory structure
            self._local_path.parent.mkdir(parents=True, exist_ok=True)

    def download_metadata(self):
        if self._local_meta.exists():
            logger.debug('Reading metadata of file %s from %s', self, self._local_meta)
            with self._local_meta.open('r') as fd:
                self._metadata.clear()
                self._metadata.update(json.load(fd))

        # Manage the bare minimum metadata. On Quetzal, this is done by the
        # Quetzal server, but here, we need to do it manually
        self._metadata.setdefault('base', {})
        base_meta = self._metadata['base']
        if 'filename' not in base_meta:
            base_meta['filename'] = self._local_path.name
        if 'path' not in base_meta:
            path = str(self._local_path.parent.relative_to(self._root))
            if path == '.':
                path = ''
            base_meta['path'] = path
        if 'id' not in base_meta:
            base_meta['id'] = self._file_id
        if 'size' not in base_meta or 'checksum' not in base_meta:
            if self._local_path.exists():
                with self._local_path.open('rb') as f:
                    checksum, size = get_readable_info(f)
                base_meta['size'] = size
                base_meta['checksum'] = checksum

    def __repr__(self):
        base_metadata = self._metadata.get('base', {})
        filename = base_metadata.get('filename', 'unnamed')
        return f'LocalFile<filename={filename}>'

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_metadata']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._metadata = collections.defaultdict(dict)

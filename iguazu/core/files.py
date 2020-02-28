""" Abstract and concrete classes to encapsulate file operations

TODO: explain here the use-cases

UC1: create a new file to fill it with new data and metadata
UC1-subcase: retrieve an existing file from its name and path
UC2: create a new file from another one as a parent
UC3: retrieve file for reading

"""


import abc
import collections
import copy
import json
import logging
import pathlib
from typing import Dict, Any, Optional

from prefect import context
from prefect.client import Secret
from quetzal.client import helpers
from quetzal.client.utils import get_data_dir, get_readable_info

from iguazu.utils import mapping_issubset


logger = logging.getLogger(__name__)


class FileAdapter(abc.ABC):
    """Abstract class for accessing files

    This class provides a key abstraction of Iguazu to simplify file
    operations, regardless of what storage support is used to store the files.
    Such storage support is referred in this documentation as the *underlying
    data backend*.

    By providing an abstract file and defining its operations, Iguazu
    programmers can develop their tasks and flows can *program to an interface*.
    This helps scaling from local to remote execution easily.

    At the moment, there are two kind of files in Iguazu: local files,
    represented by :py:class:`LocalFile` and stored in a local disk, and remote
    files stored on Quetzal, represented by :py:class:`QuetzalFile` and stored
    somewhere in the cloud.

    Each file has an associated metadata dictionary that provides additional,
    modifiable information about said file. These metadata entries can be used
    before, during or after a Iguazu flow to query or filter a dataset, define
    dynamically which tasks will be executed, or simply to keep track of how a
    file was generated.

    """

    @abc.abstractmethod
    def __init__(self, *, filename, path, temporary, **kwargs):
        """ Create a new FileAdapter with empty data and metadata

        Implement and use this method for the use case 1.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def find(*, filename, path, metadata, **kwargs) -> Optional['FileAdapter']:
        pass

    @staticmethod
    @abc.abstractmethod
    def retrieve(*, file_id, **kwargs) -> Optional['FileAdapter']:
        pass

    @property
    @abc.abstractmethod
    def file(self) -> pathlib.Path:
        """Reference to the underlying data file as a :py:class:`pathlib.Path`

        Use this property to obtain a :py:class:`pathlib.Path` object that
        points to the file represented by this object, which can be opened,
        read or written as needed.

        Using this property has a side-effect on the instance: if the file
        contents are not available locally and the file exists on its
        underlying data backend, they will be downloaded. However, it is
        possible that no download is performed because the file is already
        cached somewhere locally. This only applies to implementations that use
        a data backend, such as :py:class:`QuetzalFile`.

        Using this property to write the contents of the
        :py:class:`pathlib.Path` does not guarantee that the file is saved on
        its associated backend. This is only guaranteed after calling the
        :py:func:`~FileAdapter.upload` method.

        """
        pass

    @property
    def file_str(self) -> str:
        """String representation of the :py:ref:`file` property

        Use this for a shorter synonym of ``str(instance.file.resolve())``.
        """
        return str(self.file.resolve())

    @property
    @abc.abstractmethod
    def basename(self) -> str:
        """ Basename of the file

        Basename is the final component of a file path. For example, the
        basename of ``"foo/bar/file.txt"`` is ``"file.txt"`

        """
        # """String representation of the :py:attr:`~FileAdapter.file` property
        #
        # This string representation is the absolute path of the
        # :py:class:`pathlib.Path` returned by :py:attr:`~FileAdapter.file`
        # property. Consequently, using this property has the same side-effects as
        # using the :py:attr:`~FileAdapter.file` property.
        #
        # Use this property when a string is required, such as the pesky
        # :py:class:`pandas.HDFStore`, which requires a string.
        #
        # """
        # return str(self.file.resolve())
        pass

    @property
    @abc.abstractmethod
    def dirname(self) -> str:
        """ Dirname of the file

        Dirname is the directory part of a the file complete path.
        For example, the dirname of ``"foo/bar/file.txt"`` is ``"foo/bar"``.

        This property does not contain the temporary or output directory that
        holds the underlying file.
        """
        pass

    @property
    @abc.abstractmethod
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        """Reference to the underlying metadata of this file

        Use this property to read or set the metadata of a file. Metadata is a
        dictionary that has at least two levels of depth. The first level is
        the family; the second level is are regular key-value pairs. See
        Quetzal's :std:doc:`design` documentation for an example of such
        organization.

        Using this property has a side-effect on the instance: if the file
        metadata is not available and the file exists on its underlying
        backend, then the metadata will be downloaded.

        Using this property to set or change the contents of the metadata does
        not guarantee that the file metadata is saved. This is only guaranteed
        after calling the :py:func:`~FileAdapter.upload` method.

        """
        pass

    @property
    @abc.abstractmethod
    def id(self) -> Optional[str]:
        """Unique string identifier of a file

        This property provides a unique string identifier for this file
        instance. When the file does not exist in its underlying backend, then
        the identifier will be ``None``. Conversely, when the identifier is not
        ``None``, it means that this file exists on its underlying backend.

        Since the identifier of a file is unique, two different instances with
        the same id are the same file. However, this does not account for any
        change on the data or metadata contents done by the user.

        """
        pass

    @property
    @abc.abstractmethod
    def empty(self) -> bool:
        """Evaluates if the file is empty

        This property will be ``True`` when the underlying data file has zero
        bytes. To determine this, it is not necessary to download the file.

        """
        pass

    def download(self):
        self.download_data()
        self.download_metadata()

    @abc.abstractmethod
    def download_data(self):
        pass

    @abc.abstractmethod
    def download_metadata(self):
        pass

    # @abc.abstractmethod
    # def make_child(self, *,
    #                filename: Optional[str] = None,
    #                path: Optional[str] = None,
    #                suffix: Optional[str] = None,
    #                extension: Optional[str] = None,
    #                temporary: bool = True) -> 'FileAdapter':
    #     """Create a new :py:class:`FileAdapter` instance based on this instance
    #
    #     This method provides a single implementation to create new files from
    #     existing ones. It will create or retrieve a :py:class:`FileAdapter`
    #     instance that inherits the same filename, path and extension as its
    #     parent (i.e. this instance), except where the parameters of this
    #     functions are set.
    #
    #     Parameters
    #     ==========
    #     filename
    #         Overrides the filename of the new file.
    #     path
    #         Overrides the path of the new file.
    #     suffix
    #         Extra string added after the filename stem but before its
    #         extension. Using this parameter overrides the filename of the new
    #         file. It can be used with the `filename` parameter, but it usually
    #         makes more sense to use the `suffix` but leaving the `filename`
    #         untouched.
    #     extension
    #         Overrides the file extension of the new file.
    #     temporary
    #         When this parameter is set to ``True``, the new file will be marked
    #         as a temporary file. Temporary files can be erased by the underlying
    #         backend. When this parameter is set to  ``False``, the file will be
    #         carefully tracked by the underlying backend.
    #
    #     Returns
    #     =======
    #     FileAdapter
    #         A file instance, either completely new because it did not exist on
    #         the underlying backend, or an instance associated to the existing
    #         file.
    #
    #     """
    #     pass

    def upload(self):
        """Save the file data and metadata on the underlying backend

        This method saves the contents of this file on its underlying backend.
        Metadata is saved as well. When the underlying backend already has the
        contents of the file stored, then no change is applied.

        """
        self.upload_data()
        self.upload_metadata()

    @abc.abstractmethod
    def upload_data(self):
        """Save the file data on the underlying backend

        Use this method to upload the contents of a file, but not its metadata.
        """
        pass

    @abc.abstractmethod
    def upload_metadata(self):
        """Upload the file metadata to the underlying backend

        Use this method when a change in the metadata needs to be persisted on
        the metadata backend, but it is not necessary to download or upload
        the file data.

        """

    @abc.abstractmethod
    def delete(self):
        """Delete the file data and metadata from the underlying backend

        Use this method sparingly. This method deletes the contents of a file
        and its metadata from its underlying backend. This is particularly
        useful to adhere to Iguazu's :ref:`guidelines` concerning hard
        failures, which should delete any existing results.

        """
        pass

    @abc.abstractmethod
    def __getstate__(self):
        pass

    @abc.abstractmethod
    def __setstate__(self, state):
        pass


class QuetzalFile(FileAdapter):
    # """
    #
    # Attributes
    # ----------
    # _client
    #     Reusable Quetzal client object. Will be initialized from a Prefect
    #     secret using :ref:`quetzal_client_from_secret`.
    # _file_id
    #     Quetzal file identifier. When this member is ``None``, it means that
    #     this file is not known to Quetzal yet.
    #
    # """

    def __init__(self, *,
                 filename: str,
                 path: Optional[str] = None,
                 workspace_id: Optional[int] = None,
                 temporary: bool = False,
                 metadata: Optional[Dict] = None,
                 **kwargs):
        # Some sanity checks
        if workspace_id is None and temporary:
            raise ValueError('Cannot create a Quetzal temporary file without an '
                             'associated workspace')

        super().__init__(filename=filename, path=path, temporary=temporary, **kwargs)

        self._client = None
        self._file_id = None
        self._workspace_id = workspace_id
        self._temporary = temporary
        self._metadata = collections.defaultdict(dict, metadata or {})
        if temporary:
            self._root = context.temp_dir
        else:
            self._root = context.output_dir
        self._local_path = pathlib.Path(self._root) / (path or '') / filename

    @staticmethod
    def find(*, filename, path, metadata, workspace_id) -> Optional['QuetzalFile']:
        logger.debug('Searching Quetzal file on workspace %s '
                     'with filename %s path %s and metadata %s',
                     workspace_id or 'global', filename, path, metadata)
        client = quetzal_client_from_secret()
        candidates = helpers.file.find(client, wid=workspace_id,
                                       filename=filename, path=path)

        if candidates:
            most_recent_detail = max(candidates, key=lambda d: d.date)
            logger.debug('File by name and path gave %d candidates. '
                         'Only the most recent one will be considered: %s',
                         len(candidates), most_recent_detail)
            if most_recent_detail.state == 'DELETED':
                logger.debug('Candidate is a deleted file, discarding')
                return None

            instance = QuetzalFile.retrieve(file_id=most_recent_detail.id, workspace_id=workspace_id)
            if instance is None:
                logger.error('Something is wrong: could not have found an instance '
                             'that does not exist!')
                raise RuntimeError('Found candidate but could not retrieve it')

            meta = instance.metadata
            if not mapping_issubset(metadata, meta):
                logger.debug('Candidate does not match requested metadata')
                return None

            logger.debug('Candidate matches state, metadata, file and path: %s',
                         instance)
            return instance

        logger.debug('No matches found')
        return None

    @staticmethod
    def retrieve(*, file_id, workspace_id=None) -> Optional['QuetzalFile']:
        client = quetzal_client_from_secret()
        meta = helpers.file.metadata(client, file_id, wid=workspace_id)
        filename = meta['base']['filename']
        path = meta['base']['path']
        state = meta['base']['state']
        if state not in ('READY', 'TEMPORARY'):
            logger.debug('Refusing to create a QuetzalFile instance from a deleted file')
            return None
        temporary = (state == 'TEMPORARY')
        # Create a bare Quetzal file...
        instance = QuetzalFile(filename=filename, path=path,
                               workspace_id=workspace_id, temporary=temporary)
        # ...and then complete its file_id and metadata
        instance._file_id = file_id
        instance._metadata.update(meta)  # Re-use previous results to avoid an extra request

        # ...finally, just check that the instance _local_path is not pointing
        # to old data to avoid confusion
        if instance._local_path.exists():
            size = instance.metadata['base']['size']
            checksum = instance.metadata['base']['checksum']
            with instance._local_path.open('rb') as fd:
                f_checksum, f_size = get_readable_info(fd)

            if (size, checksum) != (f_size, f_checksum):
                logger.debug('File %s already exists locally in %s,'
                             'but its size and checksum differ from Quetzal '
                             'metadata. Erasing local file...', file_id, instance.file)
                instance._local_path.unlink()
        return instance

    @property
    def file(self) -> pathlib.Path:
        if not self._local_path.exists():
            self.download_data()
        return self._local_path

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
        if self._file_id is not None:
            size = self.metadata['base']['size']
        else:
            size = self.file.stat().st_size
        return size == 0

    @property
    def client(self):
        if self._client is None:
            self._client = quetzal_client_from_secret()
        return self._client

    @property
    def workspace_id(self):
        return self._workspace_id

    # def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=True) -> 'QuetzalFile':
    #     # TODO: define what metadata gets inherited!
    #     if 'temp_dir' not in context or context.temp_dir is None:
    #         raise RuntimeError('Cannot create new file without a "temp_dir" on '
    #                            'the prefect context')
    #     temp_dir = pathlib.Path(context.temp_dir)
    #
    #     # Create a new file with the help of pathlib
    #     # First, the path
    #     base_metadata = self.metadata['base']
    #     if path is None:
    #         new = temp_dir / pathlib.PosixPath(base_metadata['path'])
    #     else:
    #         new = temp_dir / pathlib.Path(path)
    #     # Then, the filename
    #     if filename is None:
    #         new = new / base_metadata['filename']
    #     else:
    #         new = new / filename
    #     # Adjust the suffix and extension
    #     suffix = suffix or ''
    #     extension = extension or new.suffix
    #     new = new.with_name(new.stem + suffix + extension)
    #
    #     # Verify if there already a child with the same name, path and parent
    #     existing_meta = self._retrieve_child_meta(str(new.relative_to(temp_dir).parent), new.name)
    #     if existing_meta:
    #         child = QuetzalFile(file_id=existing_meta['base']['id'],
    #                             workspace_id=self._workspace_id,
    #                             **self._client_kwargs)
    #         child._metadata = existing_meta
    #         # Propagate parent metadata (drop base metadata, drop all ids)
    #         parent_metadata = copy.deepcopy(self._metadata)
    #         for family in parent_metadata:
    #             parent_metadata[family].pop('id', None)
    #         parent_metadata.pop('base', None)
    #         if 'iguazu' in parent_metadata:
    #             parent_metadata['iguazu'].pop('parents', None)
    #         child._metadata = _deep_update(child._metadata, parent_metadata)
    #         child._workspace_id = self._workspace_id
    #         return child
    #
    #     # Create new child adapter class and propagate metadata
    #     child = QuetzalFile(file_id=None,
    #                         workspace_id=self._workspace_id,
    #                         **self._client_kwargs)
    #     child._metadata = copy.deepcopy(self._metadata)
    #     if not isinstance(child._metadata, collections.defaultdict):
    #         tmp = collections.defaultdict(dict)
    #         tmp.update(child._metadata)
    #         child._metadata = tmp
    #     child._metadata.pop('base', None)
    #     child._metadata['base']['filename'] = new.name
    #     child._metadata['base']['path'] = str(new.relative_to(temp_dir).parent)
    #     # unset all id columns
    #     for family in child._metadata:
    #         child._metadata[family].pop('id', None)
    #     # unset iguazu state
    #     # no longer needed, iguazu.Task sets the default metadata
    #     #child._metadata['iguazu'].pop('state', None)
    #     # link child to parent
    #     # child._metadata['iguazu']['parents'] = base_metadata['id']
    #
    #     child._temporary = temporary
    #     # If we are creating a new child, but there is already a file with that
    #     # name, we need to clear it to avoid confusion with old results
    #     if new.exists():
    #         new.unlink()
    #     new.parent.mkdir(parents=True, exist_ok=True)  # TODO: consider a better solution
    #     child._local_path = new
    #
    #     return child

    # def _retrieve_child_meta(self, path, filename):
    #     logger.info('Retrieving possible child')
    #     parent_id = self._file_id
    #     candidates = helpers.file.find(self.client, wid=self._workspace_id, path=path, filename=filename)
    #     logger.info('File by name and path gave %d candidates', len(candidates))
    #     for file_detail in sorted(candidates, key=lambda d: d.date, reverse=True):
    #         meta = helpers.file.metadata(self.client, file_detail.id, wid=self._workspace_id)
    #         state = meta['base'].get('state', None)
    #         parents = meta.get('iguazu', {}).get('parents', [])
    #         if parent_id in parents and state != 'DELETED':
    #             logger.info('Found a match with same parent %s', meta['base'])
    #             return meta
    #     logger.info('No candidate matches')
    #     return None

    def upload_data(self):
        if self._file_id is not None:
            logger.debug('File already has an id, no need to upload to Quetzal')
        elif not self._local_path.exists():
            # elif self._local_path is None or not self._local_path.exists():
            logger.error('Something is wrong: uploading a file that does not exist')
            raise RuntimeError('Cannot upload if file does not exist')
        else:
            logger.debug('Uploading file %s to Quetzal', self._local_path)
            with self._local_path.open('rb') as fd:
                details = helpers.workspace.upload(self.client, self._workspace_id, fd,
                                                   path=self.dirname,
                                                   temporary=self._temporary)
            self._file_id = details.id
            logger.debug('File was successfully uploaded and now is id=%s', self._file_id)

    def upload_metadata(self):
        metadata = copy.deepcopy(self.metadata)
        for family in metadata:
            if 'id' in metadata[family]:
                # The id metadata is not modifyable
                metadata[family].pop('id')
            if family == 'base':
                # The base family only admits changes in path and filename
                metadata[family] = {k: v for k, v in metadata[family].items() if k in ('path', 'filename')}
        helpers.workspace.update_metadata(self.client, self._workspace_id, self._file_id, metadata)
        # unset the metadata so that next time it is refreshed
        self._metadata.clear()

    def delete(self):
        logger.debug('Deleting file %s from Quetzal', self)
        if self._local_path.exists():
            logger.debug('Local copy of data file exists at %s. Deleting it as well',
                         self._local_path)
            self._local_path.unlink()
        if self._file_id is not None:
            logger.debug('Sending request to delete to workspace %s', self._workspace_id)
            helpers.file.delete(self.client, self._file_id, self._workspace_id)
            self._file_id = None
        self._metadata.clear()

    def download_data(self):
        if self._file_id is not None and not self._local_path.exists():
            # File exists in quetzal
            logger.debug('Downloading %s -> %s', self._file_id, self._local_path)
            helpers.file.download(self.client,
                                  self._file_id,
                                  self._workspace_id,
                                  output=self._local_path)
            logger.debug('Downloaded %s -> %s', self._file_id, self._local_path)
        else:
            # File does not exist in quetzal, it is probable a new file
            # ... here, just create the directory structure
            self._local_path.parent.mkdir(parents=True, exist_ok=True)

    def download_metadata(self):
        if self._file_id is not None:
            quetzal_metadata = helpers.file.metadata(self.client, self._file_id, self._workspace_id)
            self._metadata.clear()
            self._metadata.update(quetzal_metadata)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_client']
        del state['_metadata']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._client = None
        self._metadata = collections.defaultdict(dict)

    def __repr__(self):
        base_metadata = self.metadata.get('base', {})
        fid = base_metadata.get('id', 'unindentified')
        filename = base_metadata.get('filename', 'unnamed')
        return f'QuetzalFile<id={fid}, filename={filename}>'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self._file_id, self._workspace_id) == (other._file_id, other._workspace_id)


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

    def __init__(self, file, base_dir):
        super().__init__()
        self._file = pathlib.Path(file)
        self._file_id = str(self._file)
        self._base_dir = pathlib.Path(base_dir)
        self._relative_dir = self._file.relative_to(base_dir).parent
        self._meta_file = self._file.with_name(self._file.name + ".json")
        if self._meta_file.exists():
            with open(self._meta_file) as json_file:
                self._metadata = json.load(json_file)
        else:
            self._metadata = collections.defaultdict(dict)  # type: Dict[str, Dict[str, Any]]

    @property
    def file(self) -> pathlib.Path:
        """ Reference to the local file as a :py:class:`pathlib.Path`

        Read the parent :py:attr:`~LocalFile.file` property documentation for
        more details on the general behavior for this property.

        Since underlying storage of a :py:class:`LocalFile` is a regular file,
        using this property does not incur in any download operation.
        However, it will create the directory structure of the file if it
        does not exist before. This is done to simplify any write operation on
        the file, which would otherwise require the user to add a lot of
        boilerplate code to verify and create the directory structure.

        """
        self._file.parent.mkdir(parents=True, exist_ok=True)
        return self._file

    @property
    def metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self._metadata:  # TODO: if json is present but not metadata, read it from there
            self._metadata['base']['filename'] = str(self._file.name)
            self._metadata['base']['path'] = str(self._file.parent)
            self._metadata['base']['id'] = self._file_id

        return self._metadata

    @property
    def id(self) -> Optional[str]:
        return str(self._file)

    def make_child(self, *, filename=None, path=None, suffix=None, extension=None, temporary=True) -> 'LocalFile':
        """ Creates a child FileAdapter that inherits from its parent's metadata.

        Parameters
        ----------
        filename: name of the FileAdapter to create. If None, the a suffix is added to the parent's FileAdapter
        and the direction is given in the context by 'temp_dir'.
        path: path relative to temp_dir where the child FileAdapter is created (eg. "/preprocessed/galvanic") . If None, the relative path is the same
        as it's parent relative to base_dir.
        suffix: suffix to add at the end of the filename (eg. "_clean"). If None, nothing is added.
        extension: extension of the child FileAdapter (eg. "hdf5", "csv", "png", ... ) . If None, the extension is the same as it's parent.
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
        child_exists = False
        if new.exists():
            child_exists = True
        # Retrieve or create child
        child = LocalFile(new, base_dir=file_dir)
        child._local_path = new
        child._temporary = temporary

        # If child has just been created, propagate metadata
        if not child_exists:
            child = LocalFile(new, base_dir=file_dir)
            child._local_path = new
            child._temporary = temporary
            # TODO: think: perhaps remove child metadata propagation
            child._metadata = copy.deepcopy(self._metadata)
            if not isinstance(child._metadata, collections.defaultdict):
                tmp = collections.defaultdict(dict)
                tmp.update(child._metadata)
                child._metadata = tmp
            child._metadata.pop('base', None)
            child._metadata['base']['filename'] = new.name
            child._metadata['base']['path'] = str(new.relative_to(file_dir).parent)
            child._metadata['base']['id'] = child._file_id
            # # NEW! and TODO: we must remove the iguazu family!
            # Response: no, the iguazu.Task takes care of setting the iguazu family
            #
            # child._metadata.pop('iguazu', None)
            # if 'iguazu' in child._metadata:
            #     del child._metadata['iguazu']
            #child._metadata['iguazu']['parents'] = [base_metadata['id']]
            # # unset iguazu state
            # child._metadata['iguazu'].pop('state', None)

        return child

    def upload(self):
        self.upload_metadata()

    def upload_metadata(self):
        # Upload on local file dumps the meta in a json
        with open(self._meta_file, 'w') as outfile:
            json.dump(self.metadata, outfile, indent=2, sort_keys=True)

    def delete(self):
        # TODO: when we update to Python 3.8, use unlink(missing_ok=True)
        #       instead of these if statements.
        if self._file.exists():
            self._file.unlink()
        if self._meta_file.exists():
            self._meta_file.unlink()

    @property
    def empty(self):
        return self.file.stat().st_size == 0

    def __repr__(self):
        base_metadata = self.metadata.get('base', {})
        filename = base_metadata.get('filename', 'unnamed')
        return f'LocalFile<filename={filename}>'


def _deep_update(dest, src):
    for k, v in src.items():
        if isinstance(v, collections.abc.Mapping):
            dest[k] = _deep_update(dest.get(k, {}), v)
        else:
            dest[k] = v
    return dest


def quetzal_client_from_secret():
    try:
        quetzal_kws = Secret('QUETZAL_CLIENT_KWARGS').get()
    except ValueError as ex:
        logger.debug('Could not retrieve prefect secret '
                     'QUETZAL_CLIENT_KWARGS due to the following exception: %s. '
                     'Falling back to environment variable-based client',
                      ex)
        quetzal_kws = {}

    return helpers.get_client(**quetzal_kws)

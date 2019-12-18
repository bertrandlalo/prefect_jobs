import abc
import collections
import copy
import json
import logging
import pathlib
from typing import Any, Dict, Optional

from prefect import context
from quetzal.client import helpers
from quetzal.client.utils import get_data_dir

logger = logging.getLogger(__name__)


class FileProxy(abc.ABC):
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
        :py:func:`~FileProxy.upload` method.

        """
        pass

    @property
    def filename(self) -> str:
        """String representation of the :py:attr:`~FileProxy.file` property

        This string representation is the absolute path of the
        :py:class:`pathlib.Path` returned by :py:attr:`~FileProxy.file`
        property. Consequently, using this property has the same side-effects as
        using the :py:attr:`~FileProxy.file` property.

        Use this property when a string is required, such as the pesky
        :py:class:`pandas.HDFStore`, which requires a string.

        """
        return str(self.file.resolve())

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
        after calling the :py:func:`~FileProxy.upload` method.

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
    def empty(self):
        """Evaluates if the file is empty

        This property will be ``True`` when the underlying data file has zero
        bytes. To determine this, it is not necessary to download the file.

        """
        pass

    @abc.abstractmethod
    def make_child(self, *,
                   filename: Optional[str] = None,
                   path: Optional[str] = None,
                   suffix: Optional[str] = None,
                   extension: Optional[str] = None,
                   temporary: bool = True) -> 'FileProxy':
        """Create a new :py:class:`FileProxy` instance based on this instance

        This method provides a single implementation to create new files from
        existing ones. It will create or retrieve a :py:class:`FileProxy`
        instance that inherits the same filename, path and extension as its
        parent (i.e. this instance), except where the parameters of this
        functions are set.

        Parameters
        ==========
        filename
            Overrides the filename of the new file.
        path
            Overrides the path of the new file.
        suffix
            Extra string added after the filename stem but before its
            extension. Using this parameter overrides the filename of the new
            file. It can be used with the `filename` parameter, but it usually
            makes more sense to use the `suffix` but leaving the `filename`
            untouched.
        extension
            Overrides the file extension of the new file.
        temporary
            When this parameter is set to ``True``, the new file will be marked
            as a temporary file. Temporary files can be erased by the underlying
            backend. When this parameter is set to  ``False``, the file will be
            carefully tracked by the underlying backend.

        Returns
        =======
        FileProxy
            A file instance, either completely new because it did not exist on
            the underlying backend, or an instance associated to the existing
            file.

        """
        # TODO: change extension
        pass

    @abc.abstractmethod
    def upload(self):
        """Save the file data and metadata on the underlying backend

        This method saves the contents of this file on its underlying backend.
        Metadata is saved as well. When the underlying backend already has the
        contents of the file stored, then no change is applied.

        """
        pass

    @abc.abstractmethod
    def delete(self):
        """Delete the file data and metadata from the underlying backend

        Use this method sparingly. This method deletes the contents of a file
        and its metadata from its underlying backend. This is particularly
        useful to adhere to Iguazu's :ref:`guidelines` concerning hard
        failures, which should delete any existing results.

        """
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
    def id(self) -> Optional[str]:
        if self._file_id is None:
            return None
        return str(self._file_id)

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
            child._wid = self._wid
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
            child._metadata[family].pop('id', None)
        # unset iguazu state
        # no longer needed, iguazu.Task sets the default metadata
        #child._metadata['iguazu'].pop('state', None)
        # link child to parent
        # child._metadata['iguazu']['parents'] = base_metadata['id']

        child._temporary = temporary
        # If we are creating a new child, but there is already a file with that
        # name, we need to clear it to avoid confusion with old results
        if new.exists():
            new.unlink()
        new.parent.mkdir(parents=True, exist_ok=True)  # TODO: consider a better solution
        child._local_path = new

        return child

    def _retrieve_child_meta(self, path, filename):
        logger.info('Retrieving possible child')
        parent_id = self._file_id
        candidates = helpers.file.find(self.client, wid=self._wid, path=path, filename=filename)
        logger.info('File by name and path gave %d candidates', len(candidates))
        for file_detail in sorted(candidates, key=lambda d: d.date, reverse=True):
            meta = helpers.file.metadata(self.client, file_detail.id, wid=self._wid)
            state = meta['base'].get('state', None)
            parents = meta.get('iguazu', {}).get('parents', [])
            if parent_id in parents and state != 'DELETED':
                logger.info('Found a match with same parent %s', meta['base'])
                return meta
        logger.info('No candidate matches')
        return None

    def upload(self):
        logger.info('Uploading %s to Quetzal', self)
        if self._file_id is not None:
            logger.info('File already has an id, no need to upload')
        elif self._local_path is None or not self._local_path.exists():
            raise RuntimeError('Cannot upload if file does not exist')
        else:
            with open(self._local_path, 'rb') as fd:
                details = helpers.workspace.upload(self.client, self._wid, fd,
                                                   path=self.metadata['base'].get('path', None) or '',
                                                   temporary=self._temporary)
            self._file_id = details.id

        self._upload_metadata()

    def _upload_metadata(self):
        metadata = copy.deepcopy(self.metadata)
        for family in metadata:
            if 'id' in metadata[family]:
                metadata[family].pop('id')
            if family == 'base':
                metadata[family] = {k: v for k, v in metadata[family].items() if k in ('path', 'filename')}
                # for k in list(metadata[family]):  # note list for in-loop modification
                #     if k not in ('path', 'filename'):
                #         metadata[family].pop(k)
        helpers.workspace.update_metadata(self.client, self._wid, self._file_id, metadata)
        # unset the metadata so that next time it is refreshed
        self._metadata.clear()

    def delete(self):
        logger.info('Deleting file %s from Quetzal', self)
        if self._local_path is not None and self._local_path.exists():
            logger.debug('Underlying data file exists at %s. Deleting it', self._local_path)
            self._local_path.unlink()
        if self._file_id is not None:
            logger.debug('Sending request delete %s at workspace %s', self._file_id, self._wid)
            self.client.workspace_file_delete(self._wid, self._file_id)
            self._file_id = None
        self._metadata.clear()

    @property
    def empty(self):
        if self._local_path is None:
            base_metadata = self.metadata.get('base', {})
            size = base_metadata.get('size', 0)
        else:
            size = self.file.stat().st_size
        return size == 0

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_local_path']
        state.pop('_metadata', None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._local_path = None
        self._metadata = collections.defaultdict(dict)

    def __repr__(self):
        base_metadata = self.metadata.get('base', {})
        fid = base_metadata.get('id', 'unindentified')
        filename = base_metadata.get('filename', 'unnamed')
        return f'QuetzalFile<id={fid}, filename={filename}>'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self._file_id, self._wid) == (other._file_id, other._wid)


class LocalFile(FileProxy):
    """File proxy implementation that uses local files

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

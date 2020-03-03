import collections
import copy
import json
import pathlib
from typing import Dict, Any, Optional

from iguazu.core.files.base import FileAdapter
from prefect import context


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

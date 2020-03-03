import abc
import pathlib
from typing import Optional, Dict, Any

from quetzal.client.utils import get_readable_info


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

    def checksum(self, stream):
        """Check if the file metadata match the contents of a stream"""
        size = self.metadata['base']['size']
        checksum = self.metadata['base']['checksum']
        f_checksum, f_size = get_readable_info(stream)
        return (size, checksum) == (f_size, f_checksum)

    @abc.abstractmethod
    def __getstate__(self):
        """ Serialize this instance (used by pickle) """
        pass

    @abc.abstractmethod
    def __setstate__(self, state):
        """ Create an instance by deserialization (used by pickle) """
        pass

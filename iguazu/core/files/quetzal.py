import collections
import copy
import functools
import logging
import pathlib
from typing import Optional, Dict, Any

from prefect import context
from prefect.client import Secret
from quetzal.client import helpers, Configuration
from quetzal.client.utils import get_data_dir

from iguazu.core.files import FileAdapter, QuetzalURL
from iguazu.utils import mapping_issubset

logger = logging.getLogger(__name__)


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
        if temporary:
            if 'temp_url' not in context:
                logger.warning('Creating a temporary file, but no temp_url found in '
                               'context. Are you creating a file outside a prefect '
                               'task or flow?')
            if not isinstance(context.temp_url, QuetzalURL):
                logger.warning('Creating a temporary file, but temp_url is not a '
                               'Quetzal URL like "quetzal://...", this seems wrong')
        else:
            if 'output_url' not in context:
                logger.warning('Creating a non-temporary file, but no output_url found in '
                               'context. Are you creating a file outside a prefect '
                               'task or flow?')
            if not isinstance(context.output_url, QuetzalURL):
                logger.warning('Creating a non-temporary file, but output_url is not a '
                               'Quetzal URL like "quetzal://...", this seems wrong')

        super().__init__(filename=filename, path=path, temporary=temporary, **kwargs)
        self._client = None
        self._file_id = None
        self._workspace_id = workspace_id
        self._temporary = temporary
        self._metadata = collections.defaultdict(dict, metadata or {})
        if temporary:
            self._root = context.temp_dir
            self._url = context.temp_url
        else:
            self._root = get_data_dir()
            self._url = context.output_url
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
                logger.debug('Candidate does not match requested metadata, discarding')
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
            with instance._local_path.open('rb') as fd:
                local_is_valid = instance.checksum(fd)
            if not local_is_valid:
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
        # return self._workspace_id
        return self._url.workspace_id

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
                if self._url.path:
                    fullpath = '/'.join([self._url.path, self.dirname])
                else:
                    fullpath = self.dirname
                details = helpers.workspace.upload(self.client, self.workspace_id, fd,
                                                   path=fullpath,
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

    def clean(self):
        logger.debug('Cleaning file %s from disk', self)
        if self._local_path.exists():
            logger.debug('Deleting file %s', self._local_path.resolve())
            self._local_path.unlink()
        else:
            logger.debug('No need to delete file %s : it does not exist',
                         self._local_path.resolve())

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
            # File does not exist in quetzal, it is probably a new file
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
        filename = base_metadata.get('filename', None)
        if not filename:
            if self._local_path is not None:
                filename = self._local_path.name
            else:
                filename = 'unnamed'
        return f'QuetzalFile<id={fid}, filename={filename}>'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self._file_id, self._workspace_id) == (other._file_id, other._workspace_id)


def quetzal_client_from_secret():
    default_config = Configuration()
    quetzal_kws = dict(
        url=default_config.host,
        username=default_config.username,
        password=default_config.password,
        api_key=default_config.api_key.get('X-API-KEY', None)
    )
    try:
        quetzal_kws = Secret('QUETZAL_CLIENT_KWARGS').get()
    except ValueError as ex:
        logger.debug('Could not retrieve prefect secret '
                     'QUETZAL_CLIENT_KWARGS due to the following exception: %s '
                     'Falling back to environment variable-based client',
                     ex)
    return _memo_quetzal_client(**quetzal_kws)


@functools.lru_cache(maxsize=1024)
def _memo_quetzal_client(**kwargs):
    """A memorized client from its kwargs

    This re-usability of Quetzal clients is important when one has a flow that
    uses many tasks that interact with Quetzal. Eventually, the system may run
    out of available connections (in reality they are socket files) and any
    Quetzal operation will fail with a weird NewConnectionError exception
    """
    return helpers.get_client(**kwargs)


@functools.lru_cache(maxsize=1024)
def resolve_workspace_name(name: str) -> int:
    logger.debug('Resolving Quetzal workspace name %s...', name)
    client = quetzal_client_from_secret()
    details, total = helpers.workspace.list_(client,
                                             name=name,
                                             deleted=False)
    if total == 0:
        raise RuntimeError(f'No workspace named "{name}" was found')
    elif total > 1:
        raise RuntimeError(f'Workspace "{name}" is not unique, there were '
                           f'{len(total)} workspaces with the same name...')

    return details[0]['id']

import copy
import logging
import os
import pathlib
from typing import Dict, Iterable, NoReturn, Optional

import pandas as pd
import prefect

import iguazu
from iguazu import __version__
from iguazu.core.exceptions import SoftPreconditionFailed, GracefulFailWithResults
from iguazu.helpers.files import FileProxy, LocalFile, _deep_update
from iguazu.helpers.states import GRACEFULFAIL
from iguazu.helpers.tasks import get_base_meta


logger = logging.getLogger(__name__)


class ListFiles(prefect.Task):
    """
    List the files located in basedir .
        TODO: Find a way to mimic Quetzal-client behavior?
    Parameters
    ----------
    basedir: local direction to list the files from.
    pattern: string with matching pattern to select the files.

    Returns
    -------
    files: a list of files matching the specified pattern.
    """

    def __init__(self, as_proxy: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._as_proxy = as_proxy

    def run(self, basedir, pattern='**/*.hdf5'):
        logger = prefect.context.get("logger")
        if not basedir:
            return []
        path = pathlib.Path(basedir)
        # regex = re.compile(regex)
        # files = [file for file in path.glob('**/*') if regex.match(file.name)]
        files = [file for file in path.glob(pattern)]
        # files.sort()
        logger.info('list_files on basedir %s found %d files to process',
                    basedir, len(files))

        if self._as_proxy:
            proxies = [LocalFile(f, base_dir=basedir) for f in files]
            return proxies

        return files


class Log(prefect.Task):

    def __init__(self, level=logging.INFO, **kwargs):
        super().__init__(**kwargs)
        self.level = level

    def run(self, input):
        self.logger.log(self.level, 'Received %s', input)


class AlwaysFail(prefect.Task):

    def __init__(self, msg=None, **kwargs):
        super().__init__(**kwargs)
        self.msg = msg or 'Always fails'

    def run(self):
        raise prefect.engine.signals.FAIL(self.msg)


class AlwaysSucceed(prefect.Task):
    def run(self):
        pass


class MergeFilesFromGroups(prefect.Task):
    """ Merge HDF5 files

    This tasks merges HDF5 with with unique groups into one file containing all
    the groups.
    """

    def __init__(self, suffix=None, status_metadata_key=None, **kwargs):
        """

        Parameters
        ----------
        suffix: str
            Suffix to add at the end of the parent file when creating its child

        kwargs:
            Keywords arguments with keys are hdf5 group to read and merge and
            values are hdf5 file proxy.
        """
        super().__init__(**kwargs)
        self.suffix = suffix or "_merged"
        self.status_key = status_metadata_key

    def run(self, parent, **kwargs) -> FileProxy:

        output = parent.make_child(temporary=False, suffix=self.suffix)
        try:
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(output.file, "a") as output_store:
                for output_group, file_proxy in kwargs.items():
                    # Inherit the contents of the "task" family only for this input
                    output.metadata['iguazu'].setdefault(output_group, {})
                    output.metadata['iguazu'][output_group].update(file_proxy.metadata.get('iguazu', {}))
                    output_group = output_group.replace("_", "/")
                    with pd.HDFStore(file_proxy.file, "r") as input_store:
                        groups = input_store.keys()
                        if len(groups) > 1:
                            # multiple groups in the HDF5, then get rid of the common path and
                            # append it to the output group.
                            common = os.path.commonprefix(input_store.keys())
                            for group in groups:
                                rel = os.path.relpath(group, common)  # TODO: all of these os.path are unix dependent! it would not work on windows
                                data = pd.read_hdf(input_store, group)
                                assert isinstance(data, pd.DataFrame)  # Protect from hdf that store something else
                                g = '/'.join([output_group, rel])
                                self.logger.debug('Saving dataframe of size %s into group %s',
                                                  data.shape, g)
                                data.to_hdf(output_store, g)
                        else:
                            data = pd.read_hdf(input_store, groups[0])
                            assert isinstance(data, pd.DataFrame)  # Protect from hdf that store something else
                            self.logger.debug('Saving dataframe of size %s into group %s',
                                              data.shape, output_group)
                            data.to_hdf(output_store, output_group)
                            # TODO: since we are using both numbers and 'bad' to set the values
                            #       of the group, this generates a pytables warning:
                            #       PerformanceWarning: your performance may suffer as PyTables
                            #       will pickle object types that it cannot map directly to c-types

            state = 'SUCCESS'
            meta = get_base_meta(self, state=state)

        except Exception as ex:
            self.logger.warning('MergeFilesFromGroups clean graceful fail', exc_info=True)
            state = 'FAILURE'
            meta = get_base_meta(self, state=state, ex=str(ex))

        output.metadata['iguazu'].update({self.name: meta, 'state': state})
        output.upload()

        # Mark parent as processed
        parent.metadata['iguazu'][self.status_key] = {
            'status': state,
            'date': str(prefect.context.scheduled_start_time),
            'version': __version__,
        }
        parent.upload()

        # graceful_fail(meta, output, state='FAILURE')

        return output


class MergeHDF5(iguazu.Task):

    def __init__(self, *,
                 suffix: str = '_merged',
                 temporary: bool = False,
                 verify_status: bool = True,
                 hdf5_family: Optional[str] = None,
                 meta_keys: Optional[Iterable[str]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.suffix = suffix
        self.temporary = temporary
        self.verify_status = verify_status
        self.hdf5_family = hdf5_family
        self.meta_keys = tuple(meta_keys or [])

    def run(self, *, parent: FileProxy, **kwargs) -> FileProxy:
        output_file = self.default_outputs(parent=parent, **kwargs)
        soft_fail = False
        journal_family = self.meta.metadata_journal_family

        with pd.HDFStore(output_file.file, 'w') as output_store:
            for name, value in kwargs.items():
                # Check if the input was a success, if it was not a success,
                # do not merge this into the results
                file_status = value.metadata.get(journal_family, {}).get('status', None)
                if self.verify_status and file_status != 'SUCCESS':
                    logger.warning('Input %s did not have a success status: %s. '
                                   'Ignoring this file on the HDF5 group merge',
                                   name, file_status)
                    soft_fail = True
                    continue

                with pd.HDFStore(value.file, 'r') as input_store:
                    for g, input_node in input_store.items():
                        # Copy the HDF5 data
                        dataframe = pd.read_hdf(input_store, key=g)
                        assert isinstance(dataframe, pd.DataFrame)  # Protect from hdf that store something else
                        dataframe.to_hdf(output_store, key=g)

                        # Propagate HDF5 metadata
                        output_node = output_store.get_node(g)
                        for meta_name in self.meta_keys:
                            if meta_name not in input_node._v_attrs:
                                logger.info('HDF5 metadata %s not present on %s', meta_name, name)
                                continue
                            output_node._v_attrs[meta_name] = input_node._v_attrs[meta_name]

        # Set the hdf5 group metadata
        if self.hdf5_family:
            with pd.HDFStore(output_file.file, 'r') as store:
                groups = list(store)
                output_file.metadata.setdefault(self.hdf5_family, {})
                output_file.metadata[self.hdf5_family]['groups'] = groups

        # Handle status with a partial result
        # This is a bit hacky because I had never thought of the use-case:
        # soft fail with these outputs
        # normally, the use case is:
        # soft fail with the default outputs
        if self.verify_status and soft_fail:
            raise GracefulFailWithResults(output_file,
                                          'One of the inputs was generated by '
                                          'a failed or soft-failed task')

        return output_file

    def preconditions(self, **inputs):
        # Implicit preconditions implemented in iguazu.Task:
        # - Previous output does not exist or task is forced
        # - Inputs are *not* marked as a failed result from a previous task
        super().preconditions(**inputs)

        # Precondition: All inputs are files
        for name, value in inputs.items():
            if not isinstance(value, FileProxy):
                raise ValueError(f'Received a non file for parameter {name}')

        # Precondition: there are no repeated groups
        groups = set()
        for name, value in inputs.items():
            # On empty files, no check is needed
            if value.empty:
                logger.debug('Input %s is an empty file, '
                             'ignoring precondition check', name)
                continue

            file_obj = value.file  # Note: This downloads the data file if it was not downloaded
            with pd.HDFStore(file_obj, 'r') as store:
                gi = set(store)
            if gi & groups:  # set intersection
                self.logger.warning('The following groups are repeated: %s',
                                    ', '.join(gi & groups))
                raise ValueError('Inputs have repeated HDF5 groups')

            # Update known groups for next iteration
            groups |= gi  # set union

    def default_outputs(self, *, parent, **inputs):
        output = parent.make_child(temporary=self.temporary,
                                   suffix=self.suffix)
        return output

    # def default_metadata(self, exception, **inputs):
    #     metadata = super().default_metadata(exception, **inputs)
    #     if self.verify_status and isinstance(exception, GracefulFailWithResults):
    #         metadata['iguazu']['status'] = 'FAILED'
    #     return metadata


class AddSourceMetadata(prefect.Task):

    def __init__(self, *,
                 new_meta: Dict,
                 source_family: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.new_meta = new_meta
        self.source_family = source_family

    def run(self, *, target: FileProxy, source: Optional[FileProxy]) -> NoReturn:

        # if 'data_2017-06-15.18.13.12' in source.id:
        #     import ipdb; ipdb.set_trace(context=21)
        #     pass

        new_meta = copy.deepcopy(self.new_meta)
        if source is not None and self.source_family is not None:
            new_meta.setdefault(self.source_family, {})
            new_meta[self.source_family]['source'] = source.id

        _deep_update(target.metadata, new_meta)
        target.upload()

        # return file
        # if 'data_2017-06-15.18.13.12' in source.id:
        #     import ipdb; ipdb.set_trace(context=21)
        #     pass
        # new_meta = copy.deepcopy(self.new_meta)
        # new_meta.setdefault(self.src_family, {})
        # new_meta[self.src_family]['source'] = source.id
        # _deep_update(file.metadata, new_meta)
        # return file

    # def default_metadata(self, exception, *, file, source):
    #     # metadata = super().default_metadata(exception, file=file, source=source)
    #     # metadata.pop('iguazu')
    #     # metadata.pop('base')
    #     # # if self.verify_status and isinstance(exception, GracefulFailWithResults):
    #     # #     metadata['iguazu']['status'] = 'FAILED'
    #     # return metadata
    #     if 'data_2017-06-15.18.13.12' in source.id:
    #         import ipdb; ipdb.set_trace(context=21)
    #         pass
    #     new_meta = copy.deepcopy(self.new_meta)
    #     new_meta.setdefault(self.src_family, {})
    #     new_meta[self.src_family]['source'] = source.id
    #     _deep_update(file.metadata, new_meta)
    #     return file.metadata


class SlackTask(prefect.tasks.notifications.SlackTask):
    """Extension of prefect's SlackTask that can gracefully fail"""
    def run(self, **kwargs):
        try:
            super().run(**kwargs)
        except Exception as ex:
            logger.info('Could not send slack notification: %s', ex)
            raise GRACEFULFAIL('Could not send notification') from None

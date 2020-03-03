import copy
import logging
import os
import pathlib
from typing import Dict, Iterable, NoReturn, Optional, List

import pandas as pd
import prefect

import iguazu
from iguazu import __version__
from iguazu.core.exceptions import GracefulFailWithResults, PreconditionFailed, SoftPreconditionFailed
from iguazu.core.files import FileAdapter, LocalFile
from iguazu.helpers.states import GRACEFULFAIL
from iguazu.helpers.tasks import get_base_meta
from iguazu.functions import specs
from iguazu.utils import deep_update


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

    def __init__(self, as_file_adapter: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._as_file_adapter = as_file_adapter

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

        if self._as_file_adapter:
            adapters = [LocalFile(f, base_dir=basedir) for f in files]
            return adapters

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
            values are hdf5 file adapter.
        """
        super().__init__(**kwargs)
        self.suffix = suffix or "_merged"
        self.status_key = status_metadata_key

    def run(self, parent, **kwargs) -> FileAdapter:

        output = parent.make_child(temporary=False, suffix=self.suffix)
        try:
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(output.file, "a") as output_store:
                for output_group, file_adapter in kwargs.items():
                    # Inherit the contents of the "task" family only for this input
                    output.metadata['iguazu'].setdefault(output_group, {})
                    output.metadata['iguazu'][output_group].update(file_adapter.metadata.get('iguazu', {}))
                    output_group = output_group.replace("_", "/")
                    with pd.HDFStore(file_adapter.file, "r") as input_store:
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
                 propagate_families: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.suffix = suffix
        self.temporary = temporary
        self.verify_status = verify_status
        self.hdf5_family = hdf5_family
        self.meta_keys = tuple(meta_keys or [])
        self.propagate_families = propagate_families or {}

    def run(self, *, parent: FileAdapter, **kwargs) -> FileAdapter:
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

                if value.empty:
                    logger.warning('Input %s is empty. Ignoring this file on '
                                   'the HDF5 group merge')
                    continue

                with pd.HDFStore(value.file, 'r') as input_store:
                    for g, input_node in input_store.items():
                        # Copy the HDF5 data
                        dataframe = pd.read_hdf(input_store, key=g)
                        assert isinstance(dataframe, pd.DataFrame)  # Protect from hdf that store something else
                        dataframe.to_hdf(output_store, key=g)

                        # # Propagate HDF5 metadata
                        # output_node = output_store.get_node(g)
                        # for meta_name in self.meta_keys:
                        #     if meta_name not in input_node._v_attrs:
                        #         logger.info('HDF5 metadata key "%s" was not present on group %s '
                        #                     'for file %s: no HDF5 metadata propagation',
                        #                     meta_name, g, value)
                        #         continue
                        #     output_node._v_attrs[meta_name] = input_node._v_attrs[meta_name]

        # Set the hdf5 group metadata
        if self.hdf5_family:
            self.logger.debug('Automatic detection of HDF5 groups that meet the standard...')
            output_file.metadata.setdefault(self.hdf5_family, {})
            with pd.HDFStore(output_file.file, 'r') as store:
                groups = list(store)
                for g in groups:

                    if g.endswith('/annotations'):
                        self.logger.debug('Ignoring group %s due to naming', g)
                        continue

                    # Check signals specs
                    try:
                        specs.check_signal_specification(pd.read_hdf(store, g))
                        self.logger.debug('Group %s meets the signal specification', g)
                        output_file.metadata[self.hdf5_family].setdefault('signals', [])
                        output_file.metadata[self.hdf5_family]['signals'].append(g)
                    except specs.SpecificationError as ex:
                        self.logger.debug('Dataframe on HDF5 under key %s is not '
                                          'a standard signals dataframe due to  %s',
                                          g, ex)

                    # Check event specs
                    try:
                        specs.check_event_specification(pd.read_hdf(store, g))
                        self.logger.debug('Group %s meets the event specification', g)
                        output_file.metadata[self.hdf5_family].setdefault('events', [])
                        output_file.metadata[self.hdf5_family]['events'].append(g)
                    except specs.SpecificationError as ex:
                        self.logger.debug('Dataframe on HDF5 under key %s is not '
                                          'a standard events dataframe due to  %s',
                                          g, ex)

                    # Check feature specs
                    try:
                        specs.check_feature_specification(pd.read_hdf(store, g))
                        self.logger.debug('Group %s meets the features specification', g)
                        output_file.metadata[self.hdf5_family].setdefault('features', [])
                        output_file.metadata[self.hdf5_family]['features'].append(g)
                    except specs.SpecificationError as ex:
                        self.logger.debug('Dataframe on HDF5 under key %s is not '
                                          'a standard features dataframe due to  %s',
                                          g, ex)

        # Propagate metadata
        for k in self.propagate_families:
            parent_meta = parent.metadata.get(k, {})
            parent_meta.pop('id', None)
            output_file.metadata[k].update(parent_meta)

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
            if not isinstance(value, FileAdapter):
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
        # output = parent.make_child(temporary=self.temporary,
        #                            suffix=self.suffix)
        output = self.create_file(
            parent=parent,
            suffix=self.suffix,
            temporary=self.temporary,
        )
        return output


class AddSourceMetadata(prefect.Task):

    def __init__(self, *, new_meta: Dict, **kwargs):
        super().__init__(**kwargs)
        self.new_meta = new_meta

    def run(self, *, file: FileAdapter) -> NoReturn:
        new_meta = copy.deepcopy(self.new_meta)
        deep_update(file.metadata, new_meta)
        # TODO: for quetzal, we are going to need a .upload_metadata method
        #       so we don't download the file for nothing
        file.upload()


class SlackTask(prefect.tasks.notifications.SlackTask):
    """Extension of prefect's SlackTask that can gracefully fail"""

    def __init__(self, preamble=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.preamble = preamble

    def run(self, **kwargs):
        message = kwargs.pop('message', None)
        if self.preamble is not None and message is not None:
            message = '\n'.join([str(self.preamble), str(message)])
        try:
            super().run(message=message, **kwargs)
        except Exception as ex:
            logger.info('Could not send slack notification: %s', ex)
            raise GRACEFULFAIL('Could not send notification') from None


class LoadDataframe(iguazu.Task):
    """Generic task that reads a HDF5 group and returns its dataframe"""

    def __init__(self, *, key: str, **kwargs):
        super().__init__(**kwargs)
        self.key = key

    def run(self, *, file: FileAdapter) -> pd.DataFrame:
        with pd.HDFStore(file.file, 'r') as store:
            contents = pd.read_hdf(store, key=self.key)
            assert isinstance(contents, pd.DataFrame)
            return contents

    def preconditions(self, *, file: FileAdapter, **inputs):
        super().preconditions(file=file, **inputs)
        if file.empty:
            raise SoftPreconditionFailed('Input file was empty')

    def default_outputs(self, **inputs):
        return None


class MergeDataframes(iguazu.Task):
    """Generic task that merges dataframes into a single CSV file"""

    def __init__(self, *, filename: str, path: str, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.path = path

    def run(self, *,
            parents: List[FileAdapter],
            dataframes: List[pd.DataFrame]) -> FileAdapter:

        output = self.default_outputs()

        merged = pd.concat([d for d in dataframes if d is not None],
                           axis='index', ignore_index=True, sort=False)
        self.logger.info('Merged dataframe to a shape of %s to %s', merged.shape, output)

        merged.to_csv(output.file, index=False)
        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        parents = original_kws['parents']
        dummy_reference = parents[0]
        # TODO remove metadata propagation
        output = dummy_reference.make_child(
            filename=self.filename, path=self.path, temporary=False)
        return output

    def preconditions(self, **kwargs) -> NoReturn:
        super().preconditions(**kwargs)
        parents = kwargs['parents']
        if len(parents) == 0:
            raise PreconditionFailed('Cannot summarize an empty dataset')

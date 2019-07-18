from typing import List, Optional

import pandas as pd
import prefect

from iguazu.functions.common import path_exists_in_hdf5
from iguazu.functions.summarize import signal_to_feature
from iguazu.helpers.files import FileProxy, QuetzalFile
from iguazu.helpers.tasks import get_base_meta


class ExtractFeatures(prefect.Task):
    """ Extract features from a signal based on period (time slices). """

    def __init__(self,
                 signals_group: str,
                 report_group: str,
                 output_group: str,
                 feature_definitions: dict,
                 sequences: Optional[list] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.signals_group = signals_group
        self.report_group = report_group
        self.output_group = output_group
        self.sequences = sequences
        self.feature_definitions = feature_definitions
        self.force = force

    def run(self,
            signals: FileProxy, report: FileProxy) -> FileProxy:

        output = signals.make_child(suffix='_features')
        # Inherit from iguazu metadata of report also
        output.metadata['iguazu'].update(report.metadata['iguazu'])
        self.logger.info('Extracting features from sequences for signals=%s -> %s',
                         signals, output)

        # Notes on parameter management
        #
        # if I wanted to admit the rewrite of a parameter foo,
        # 1. Add foo to run parameter as an optional parameter with default None
        # 2.a Manage None with `foo = foo or self.foo`
        #
        # If I wanted to admit a global context value of parameter foo
        # 2.b `foo = foo or self.foo or context.get('foo', None)`
        #
        # Finally, if a default value is needed
        # 2.c `foo = foo or self.foo or context.get('foo', 'default_value')`
        #
        # In the following lines, we are not following these ideas yet. Maybe later.
        signals_group = self.signals_group  # No default value is given here
        report_group = self.report_group  # No default value is given here
        output_group = self.output_group  # No default value is given here

        # Our current force detection code
        if not self.force and path_exists_in_hdf5(output.file, output_group):
            # TODO: consider a function that uses a FileProxy, in particular a
            #       QuetzalFile. In this case, we could read the metadata
            #       instead of downloading the file!

            # Until https://github.com/PrefectHQ/prefect/issues/1163 is fixed,
            # this is the only way to skip with results
            # skip = SkippedResult('Output already exists, skipping', result=output)
            # raise ENDRUN(state=skip)
            return output

        signals_file = signals.file.resolve()
        report_file = report.file.resolve()

        with pd.option_context('mode.chained_assignment', None), \
             pd.HDFStore(signals_file, 'r') as signals_store, \
                pd.HDFStore(report_file, 'r') as report_store:
            try:
                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signals_store, signals_group)
                if df_signals.empty:
                    raise Exception(
                        "Received empty signals dataframe. ")  # Todo: Handle FAIL in previous tasks to avoid having to check the emptyness here.
                df_report = pd.read_hdf(report_store, report_group)
                if df_report.empty:
                    raise Exception(
                        "Received empty reports dataframe. ")  # Todo: Handle FAIL in previous tasks to avoid having to check the emptyness here.
                features = signal_to_feature(df_signals, df_report,
                                             feature_definitions=self.feature_definitions, sequences=self.sequences)
                meta = get_base_meta(self, state='SUCCESS')

            except Exception as ex:
                self.logger.warning('Report VR sequences graceful fail: %s', ex)
                features = pd.DataFrame()
                meta = get_base_meta(self, state='FAILURE', exception=str(ex))

        # TODO: re-code the failure handling with respect to a task parameter
        # if fail_mode == 'grace': ==> generate empty dataframe, set metadata, return file (prefect raises success)
        # if fail_mode == 'skip':  ==> generate empty dataframe, set metadata, raise skip
        # if fail_mode == 'fail':  ==> raise exception as it arrives

        # Manage output, save to file
        output_file = output.file
        with pd.HDFStore(output_file, 'w') as output_store:
            features.to_hdf(output_store, output_group)
        # Set meta on FileProxy so that Quetzal knows about this metadata
        # output.metadata['task'][self.__class__.__name__] = meta
        # keep trace of parent tasks
        output.metadata['iguazu'].update({self.name: meta})

        output.upload()

        #graceful_fail(meta, output, state='FAILURE')

        return output


class SummarizePopulation(prefect.Task):
    def __init__(self, groups, axis_name='sequence', **kwargs):
        super().__init__(**kwargs)
        self.groups = {group.replace('_', '/'): groups[group] for group in groups}
        self.axis_name = axis_name

    def run(self, files: List[FileProxy]) -> Optional[FileProxy]:

        if not files:
            self.logger.warning("SummarizePopulation received an empty list. ")
            return None

        parent = files[0]
        output = parent.make_child(filename=None, path=None, suffix="_population",
                                   extension=".csv", temporary=False)
        output._metadata.clear()

        data_list_population = []
        for file in files:
            if file.metadata['iguazu']['state'] != 'SUCCESS':
                continue
            # TODO: make file_id or some abstract id property in FileProxy to
            #       avoid this manual management according to the proxy type
            if isinstance(file, QuetzalFile):
                file_id = file._file_id
            else:  # LocalFile
                file_id = file._file.stem
            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(file._file, 'r') as store:
                data_summary_file = pd.DataFrame()
                for group, columns in self.groups.items():
                    data = pd.read_hdf(store, group, columns=columns)
                    data_summary_file = data_summary_file.join(data, how="outer")
                if not data_summary_file.empty:
                    data_summary_file.loc[:, 'file_id'] = file_id
                    data_list_population.append(data_summary_file)

        data_output = pd.concat(data_list_population, axis=0)
        data_output = data_output.rename_axis(self.axis_name).reset_index()
        data_output.to_csv(output.file)

        output.upload()
        return output

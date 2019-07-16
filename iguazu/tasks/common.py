import os
import pathlib
import logging

import pandas as pd
import prefect

from iguazu.helpers.files import FileProxy
from iguazu.helpers.files import LocalFile


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
    ''' Merge HDF5 files with unique groups in one file containing all the groups.
    '''

    def __init__(self, suffix=None, **kwargs):
        '''

        Parameters
        ----------
        suffix: str
            Suffix to add at the end of the parent file when creating its child

        kwargs:
            Keywords arguments with keys are hdf5 group to read and merge and
            values are hdf5 file proxy.
        '''
        super().__init__(**kwargs)
        self.suffix = suffix or "_merged"

    def run(self, parent, **kwargs) -> FileProxy:

        output = parent.make_child(temporary=False, suffix=self.suffix)
        with pd.option_context('mode.chained_assignment', None), \
             pd.HDFStore(output.file, "a") as output_store:
            for output_group, file_proxy in kwargs.items():
                output.metadata['task'].setdefault(output_group, {})
                output.metadata['task'][output_group].update(file_proxy.metadata)
                output_group = output_group.replace("_", "/")
                with pd.HDFStore(file_proxy.file, "r") as input_store:
                    groups = input_store.keys()
                    if len(groups) > 1:
                        # multiple groups in the HDF5, then get rid of the common path and
                        # append it to the output group.
                        common = os.path.commonprefix(input_store.keys())
                        for group in groups:
                            rel = os.path.relpath(group, common)
                            data = pd.read_hdf(input_store, group)
                            data.to_hdf(output_store, os.path.join(output_group, rel))
                    else:
                        data = pd.read_hdf(input_store, groups[0])
                        data.to_hdf(output_store, output_group)

            output.upload()
            return output

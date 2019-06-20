from typing import List, Union
import pathlib
import os

from prefect import task, context
import prefect

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
        logger = context.get("logger")
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
            proxies = [LocalFile(f) for f in files]
            return proxies

        return files


@task()
def list_files(basedir):#, pattern):#="**/*.hdf5"):
    logger = context.get("logger")
    pattern = '**/*.hdf5'
    if not basedir:
        return []
    path = pathlib.Path(basedir)
    #regex = re.compile(regex)
    #files = [file for file in path.glob('**/*') if regex.match(file.name)]
    files = [file for file in path.glob(pattern)]
    #files.sort()
    logger.info('list_files on basedir %s found %d files to process',
                basedir, len(files))
    return files


@task
def convert_to_file_proxy(rows: Union[str, List[str]]) -> Union[LocalFile, List[LocalFile]]:
    is_list = isinstance(rows, list)
    if not is_list:
        rows = [rows]
    file_proxies = []
    for row in rows:
        file = LocalFile(row)
        file_proxies.append(file)

    if not is_list:
        return file_proxies[0]
    return file_proxies


@task()
def io_filenames(filename, output_dir=None):
    """

    Parameters
    ----------
    filename
    output_dir

    Returns
    -------

    """
    input_filename = filename
    output_dir = output_dir or os.path.dirname(filename)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    output_filename = os.path.join(output_dir, os.path.basename(input_filename))
    return {"in": input_filename, "out": output_filename}

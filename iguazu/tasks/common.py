import pathlib

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

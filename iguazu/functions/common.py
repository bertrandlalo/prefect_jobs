import pathlib

import pandas as pd


def safe_read_hdf5(filename, path):
    """
    Read a HDF5 file given its file name and path, in "read mode". If the Key does not exists, it returns None.
    # TODO: This utilities should be in datascience_utils?
    Parameters
    ----------
    filename: name of the file to read.
    path: path to the data.

    Returns
    -------
    DataFrame or None
    """
    with pd.HDFStore(filename, "r") as store:
        try:
            return pd.read_hdf(store, path)
        except KeyError:
            return None


def path_exists_in_hdf5(filename, group):
    """
    Checks whether a given group exists in a HDF5 file.
    # TODO: This utilities should be in datascience_utils?
    Parameters
    ----------
    filename: name of the file to read.
    group: group name.

    Returns
    -------
    boolean. True if the path exists, else False.
    """
    path = pathlib.Path(filename)
    if not path.exists():
        return False
    with pd.HDFStore(filename, "r") as store:
        return group in store


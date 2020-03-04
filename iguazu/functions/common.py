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


def verify_monotonic(dataframe, name=None):
    """ Raise an exception when a dataframe's index is not monotonic

    Monotonic indices are a pre-condition for many verifications in
    our code. Since pandas can have an index that has been reordered
    (and perhaps the programmer is not aware of this), this function
    can help us catch and prevent nasty bugs.

    Parameters
    ----------
    dataframe
        Dataframe, Series or an object with an index attribute
    name
        Name prepended to the exception when the verification fails

    Returns
    -------
    None

    Raises
    ------
    ValueError
        When the index is not monotonic

    """
    name = name or 'dataframe'
    if not dataframe.index.is_monotonic:
        raise ValueError(f'{name} index should be monotonic')

import pathlib
import os

from prefect import task, context
logger = context.get("logger")


@task()
def list_files(basedir, pattern="**/*.hdf5"):
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
    path = pathlib.Path(basedir)
    #regex = re.compile(regex)
   #files = [file for file in path.glob('**/*') if regex.match(file.name)]
    files = [file for file in path.glob(pattern)]
    #files.sort()
    print("List {N} files to process.".format(N=str(len(files))))
    return files

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
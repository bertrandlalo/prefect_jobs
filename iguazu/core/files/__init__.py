""" Abstract and concrete classes to encapsulate file operations

TODO: explain here the use-cases

UC1: create a new file to fill it with new data and metadata
UC1-subcase: retrieve an existing file from its name and path
UC2: create a new file from another one as a parent
UC3: retrieve file for reading

"""

import pathlib
import urllib.parse
from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class LocalURL:
    path: pathlib.Path
    backend: str = 'local'


@dataclass
class QuetzalURL:
    workspace_name: str
    workspace_id: Optional[int]
    backend: str = 'quetzal'

    def resolve(self) -> 'QuetzalURL':
        return QuetzalURL(workspace_name=self.workspace_name,
                          workspace_id=self.workspace_id or resolve_workspace_name(self.workspace_name),
                          backend=self.backend)


def parse_data_url(url: str) -> Union[LocalURL, QuetzalURL]:
    parsed = urllib.parse.urlparse(url)

    if parsed.scheme == 'quetzal':
        tmp = QuetzalURL(workspace_name=parsed.netloc, workspace_id=None)
        result = tmp.resolve()
        return result
    elif parsed.scheme == 'file':
        if parsed.netloc == '':
            # This happens with absolute paths like 'file:///Users/...'
            tmp = pathlib.Path(parsed.path)
        else:
            # When netloc is not empty, the path will have a trailing slash
            tmp = pathlib.Path(parsed.netloc) / pathlib.Path(parsed.path[1:])
        result = LocalURL(path=tmp.resolve())
        return result
    else:
        raise ValueError(f'Unsupported data URL "{url}" due to unknown scheme "{parsed.scheme}"')


# Late imports to avoid circular dependencies
from .base import FileAdapter
from .local import LocalFile
from .quetzal import resolve_workspace_name, QuetzalFile


__all__ = ['FileAdapter', 'LocalFile', 'LocalURL', 'QuetzalFile', 'QuetzalURL']

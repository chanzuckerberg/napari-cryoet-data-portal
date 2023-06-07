"""IO utilities for abstracting paths across S3, HTTPS, and a local filesystem."""

import json
import os
from typing import Any, Callable, Dict, List, Tuple

from s3fs import S3FileSystem


def list_dir(path: str) -> Tuple[str, ...]:
    """Returns the names of the contents of a directory-like path."""
    names = _list_dir_s3(path) if _is_s3(path) else os.listdir(path)
    return tuple(sorted(names))


def path_exists(path: str) -> bool:
    """Returns true if the given path exists, false otherwise."""
    return _path_exists_s3(path) if _is_s3(path) else os.path.exists(path)


def get_open(path: str) -> Callable[[str], Any]:
    """Returns a function to open a file at the given path."""
    if _is_s3(path):
        s3 = S3FileSystem(anon=True)
        return s3.open
    return open


def s3_to_https(path: str) -> str:
    """Converts an S3 URI to the equivalent CloudFront HTTPS URI."""
    return path.replace(
        "s3://cryoet-data-portal-public",
        "https://files.cryoetdataportal.cziscience.com",
    )


def read_json(path: str) -> Dict[str, Any]:
    """Reads JSON from the given path."""
    open_ = get_open(path)
    with open_(path) as f:
        return json.load(f)


def _is_s3(path: str) -> bool:
    return path.startswith("s3://")


def _path_exists_s3(path: str) -> bool:
    s3 = S3FileSystem(anon=True)
    return s3.exists(path)


def _list_dir_s3(path: str) -> List[str]:
    s3 = S3FileSystem(anon=True)
    bucket_path = path.replace("s3://", "")
    return [p.split("/")[-1] for p in s3.ls(bucket_path)]

"""Functions to read data from the portal into napari types."""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import ndjson
from napari_ome_zarr import napari_get_reader
from npe2.types import FullLayerData, PathOrPaths, ReaderFunction

from napari_cryoet_data_portal._io import get_open, read_json, s3_to_https


OBJECT_COLOR = {
    'ribosome': 'red',
    'ribosome, 80 s': 'red',
    'fatty acid synthase': 'darkblue',
}
DEFAULT_OBJECT_COLOR = 'red'


def tomogram_ome_zarr_reader(path: PathOrPaths) -> Optional[ReaderFunction]:
    return _read_many_tomograms_ome_zarr


def _read_many_tomograms_ome_zarr(paths: PathOrPaths) -> List[FullLayerData]:
    if isinstance(paths, str):
        paths = [paths]
    return [read_tomogram_ome_zarr(p) for p in paths]


def read_tomogram_metadata(path: str) -> Dict[str, Any]:
    return read_json(path)


def read_tomogram_ome_zarr(path: str) -> FullLayerData:
    """Reads a napari image layer from a tomogram in the OME-Zarr format.

    Parameters
    ----------
    path : str
        The path of the top of the OME-Zarr hierarchy.

    Returns
    -------
    napari layer data tuple
        The data, attributes, and type name of the image layer that would be
        returned by `Image.as_layer_data_tuple`.

    Examples
    --------
    >>> from napari.layers import Image
    >>> data, attrs, _ = read_tomogram_ome_zarr('s3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_026.zarr')
    >>> image = Image(data, **attrs)
    """
    path = s3_to_https(path)
    reader = napari_get_reader(path)
    layers = reader(path)
    return layers[0]


def points_annotations_reader(path: PathOrPaths) -> Optional[ReaderFunction]:
    """napari plugin entry point for reading points annotations.

    Parameters
    ----------
    path : str or sequence of str
        The path or paths of the annotation JSON file(s) to read.

    Returns
    -------
    A function that can be called with the same path parameter to produce
    a list of napari points layer data tuples.

    See also
    --------
    read_points_annotations_json : reads napari layer data from one annotation JSON file.

    Examples
    --------
    >>> path = ['julia_mahamid-ribosome-1.0.json', 'julia_mahamid-fatty_acid_synthase-1.0.json']
    >>> reader = points_annotations_reader(path)
    >>> data, attrs, _ = reader(path)
    """
    return _read_many_points_annotations


def _read_many_points_annotations(paths: PathOrPaths) -> List[FullLayerData]:
    if isinstance(paths, str):
        paths = [paths]
    return [read_points_annotations_json(p) for p in paths]


def read_points_annotations_json(path: str) -> FullLayerData:
    """Reads a napari points layer from one annotation JSON File.

    Parameters
    ----------
    path : str
        The path of the annotation JSON file to read.

    Returns
    -------
    napari layer data tuple
        The data, attributes, and type name of the points layer that would be
        returned by `Points.as_layer_data_tuple`.

    Examples
    --------
    >>> from napari.layers import Points
    >>> data, attrs, _ = read_points_annotations_json('julia_mahamid-ribosome-1.0.json')
    >>> points = Points(data, **attrs)
    """
    data: List[Tuple[float, float, float]] = []
    open_ = get_open(path)
    with open_(path) as f:
        metadata = json.load(f)
    data_dir = os.path.dirname(path)
    for sub_file in metadata["files"]:
        sub_name = sub_file["file"]
        sub_path = f"{data_dir}/{sub_name}"
        sub_data = _read_points_annotations_ndjson(sub_path)
        data.extend(sub_data)
    anno_object = metadata["annotation_object"]
    name = anno_object["name"]
    face_color = OBJECT_COLOR.get(name.lower(), DEFAULT_OBJECT_COLOR)
    attributes = {
        "name": name,
        "metadata": metadata,
        "size": 14,
        "face_color": face_color,
        "opacity": 0.5,
        "out_of_slice_display": True,
    }
    return data, attributes, "points"


def _read_points_annotations_ndjson(
    path: str,
) -> List[Tuple[float, float, float]]:
    data: List[Tuple[float, float, float]] = []
    open_ = get_open(path)
    with open_(path) as f:
        sub_data = [
            _annotation_to_point(annotation)
            for annotation in ndjson.load(f)
            if annotation["type"] == "point"
        ]
        data.extend(sub_data)
    return data


def _annotation_to_point(
    annotation: Dict[str, Any]
) -> Tuple[float, float, float]:
    # Related images are in zyx order, so keep these consistent.
    coords = annotation["location"]
    return (coords["z"], coords["y"], coords["x"])

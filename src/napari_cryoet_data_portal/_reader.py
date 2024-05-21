"""Functions to read data from the portal into napari types."""

import warnings
from typing import Any, Dict, Generator, List, Optional, Tuple
import fsspec

import numpy as np
import ndjson
from napari_ome_zarr import napari_get_reader
from npe2.types import FullLayerData, PathOrPaths, ReaderFunction
from cryoet_data_portal import Annotation, AnnotationFile, Tomogram
from cmap import Colormap
from napari.utils.colormaps import direct_colormap

from napari_cryoet_data_portal._logging import logger

# Maps integer value of Annotation.object_id to a color.
OBJECT_COLORMAP = Colormap("colorbrewer:set1_8")
# Fallback color when ID cannot be parsed.
DEFAULT_OBJECT_COLOR = np.array(OBJECT_COLORMAP(0).rgba)


def _annotation_color(annotation: Annotation) -> np.ndarray:
    """Maps an annotation to a color based on its object_id."""
    try:
        object_id = int(annotation.object_id.split(":")[-1])
    except RuntimeError as e:
        logger.error("Failed to parse integer from object_id: %s\%s", annotation.object_id, e)
        return DEFAULT_OBJECT_COLOR
    color = OBJECT_COLORMAP(object_id % len(OBJECT_COLORMAP.color_stops))
    return np.array(color.rgba)


def tomogram_ome_zarr_reader(path: PathOrPaths) -> Optional[ReaderFunction]:
    """napari plugin entry point for reading tomograms in the OME-Zarr format.

    Parameters
    ----------
    path : str or sequence of str
        The path or paths of the OME-Zarr directories containing tomograms.

    Returns
    -------
    A function that can be called with the same path parameter to produce
    a list of napari image layer data tuples.

    See also
    --------
    read_tomogram_ome_zarr : reads napari layer data from one OME-Zarr directory

    Examples
    --------
    >>> dataset_dir = 's3://cryoet-data-portal-public/10000'
    >>> path = (
        f'{dataset_dir}/TS_026/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_026.zarr',
        f'{dataset_dir}/TS_027/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_027.zarr',
    )
    >>> reader = tomogram_ome_zarr_reader(path)
    >>> layers = reader(path)
    """
    return _read_many_tomograms_ome_zarr


def _read_many_tomograms_ome_zarr(paths: PathOrPaths) -> List[FullLayerData]:
    if isinstance(paths, str):
        paths = [paths]
    return [read_tomogram_ome_zarr(p) for p in paths]


def read_tomogram_ome_zarr(path: str) -> FullLayerData:
    """Reads a napari image layer from a tomogram in the OME-Zarr format.

    Parameters
    ----------
    path : str
        The path of the OME-Zarr directory.

    Returns
    -------
    napari layer data tuple
        The data, attributes, and type name of the image layer that would be
        returned by `Image.as_layer_data_tuple`.

    Examples
    --------
    >>> path = 's3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48/CanonicalTomogram/TS_026.zarr'
    >>> data, attrs, _ = read_tomogram_ome_zarr(path)
    >>> image = Image(data, **attrs)
    """
    reader = napari_get_reader(path)
    layers = reader(path)
    return layers[0]


def read_tomogram(tomogram: Tomogram) -> FullLayerData:
    """Reads a napari image layer from a tomogram.

    Parameters
    ----------
    tomogram : Tomogram
        The tomogram to read.

    Returns
    -------
    napari layer data tuple
        The data, attributes, and type name of the image layer that would be
        returned by `Image.as_layer_data_tuple`.

    Examples
    --------
    >>> client = Client()
    >>> tomogram = client.find_one(Tomogram)
    >>> data, attrs, _ = read_tomogram(tomogram)
    >>> image = Image(data, **attrs)
    """
    data, attributes, layer_type = read_tomogram_ome_zarr(tomogram.https_omezarr_dir)
    attributes["name"] = tomogram.name
    attributes["metadata"] = tomogram.to_dict()
    return data, attributes, layer_type


def points_annotations_reader(path: PathOrPaths) -> Optional[ReaderFunction]:
    """napari plugin entry point for reading points annotations.

    Parameters
    ----------
    path : str or sequence of str
        The path or paths of the annotation NDJSON file(s) to read.

    Returns
    -------
    A function that can be called with the same path parameter to produce
    a list of napari points layer data tuples.

    See also
    --------
    read_points_annotations_json : reads napari layer data from one annotation JSON file.

    Examples
    --------
    >>> annotation_dir = 's3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48/Annotations'
    >>> path = (
        f'{annotation_dir}/sara_goetz-ribosome-1.0.ndjson',
        f'{annotation_dir}/sara_goetz-fatty_acid_synthase-1.0.ndjson',
    )
    >>> reader = points_annotations_reader(path)
    >>> layers = reader(path)
    """
    return _read_many_points_annotations_ndjson


def _read_many_points_annotations_ndjson(paths: PathOrPaths) -> List[FullLayerData]:
    if isinstance(paths, str):
        paths = [paths]
    return [read_points_annotations_ndjson(p) for p in paths]


def read_points_annotations_ndjson(path: str) -> FullLayerData:
    """Reads a napari points layer from an NDJSON annotation file.

    Parameters
    ----------
    path : str
        The path to the NDJSON annotations file.

    Returns
    -------
    napari layer data tuple
        The data, attributes, and type name of the points layer that would be
        returned by `Points.as_layer_data_tuple`.

    Examples
    --------
    >>> path = 's3://cryoet-data-portal-public/10000/TS_026/Tomograms/VoxelSpacing13.48/Annotations/sara_goetz-ribosome-1.0.json'
    >>> data, attrs, _ = read_points_annotations_ndjson(path)
    >>> points = Points(data, **attrs)
    """
    data = _read_points_data(path)
    attributes = {
        "name": "annotations",
        "size": 14,
        "face_color": DEFAULT_OBJECT_COLOR,
        "opacity": 0.5,
        # Disable out-of-slice display because of:
        # https://github.com/napari/napari/issues/6914
        "out_of_slice_display": False,
    }
    return data, attributes, "points"


def read_annotation(annotation: Annotation, *, tomogram: Optional[Tomogram] = None) -> FullLayerData:
    """Reads a napari points layer from an annotation.

    Parameters
    ----------
    annotation : Annotation
        The tomogram annotation.
    tomogram : Tomogram, optional
        The associated tomogram, which may be used for other metadata.

    Returns
    -------
    napari layer data tuple
        The data, attributes, and type name of the points layer that would be
        returned by `Points.as_layer_data_tuple`.

    Examples
    --------
    >>> client = Client()
    >>> annotation = client.find_one(Annotation)
    >>> data, attrs, _ = read_annotation(annotation)
    >>> points = Points(data, **attrs)
    """
    warnings.warn(
        "read_annotation is deprecated from v0.4.0 because of Annotation schema changes. "
        "Use read_annotation_files instead.",
        category=DeprecationWarning)
    point_paths = tuple(
        f.https_path
        for f in annotation.files
        if f.shape_type == "Point"
    )
    if len(point_paths) > 1:
        logger.warn("Found more than one points annotation. Using the first.")
    data, attributes, layer_type = read_points_annotations_ndjson(point_paths[0])
    name = annotation.object_name
    if tomogram is None:
        attributes["name"] = name
    else:
        attributes["name"] = f"{tomogram.name}-{name}"
    attributes["metadata"] = annotation.to_dict()
    attributes["face_color"] = _annotation_color(annotation)
    return data, attributes, layer_type


def read_annotation_files(annotation: Annotation, *, tomogram: Optional[Tomogram] = None) -> Generator[FullLayerData, None, None]:
    """Reads multiple annotation layers.

    Parameters
    ----------
    annotation : Annotation
        The tomogram annotation.
    tomogram : Tomogram, optional
        The associated tomogram, which may be used for other metadata.

    Yields
    -------
    napari layer data tuple
        The data, attributes, and type name of the layer that would be
        returned by `Points.as_layer_data_tuple` or `Labels.as_layer_data_tuple`.

    Examples
    --------
    >>> client = Client()
    >>> annotation = client.find_one(Annotation)
    >>> for data, attrs, typ in read_annotation_files(annotation):
            layer = Layer.create(data, attrs, typ)
    """
    for f in annotation.files:
        if (f.shape_type in ("Point", "OrientedPoint")) and (f.format == "ndjson"):
            yield _read_points_annotation_file(f, anno=annotation, tomogram=tomogram)
        elif (f.shape_type == "SegmentationMask") and (f.format == "zarr"):
            yield _read_labels_annotation_file(f, anno=annotation, tomogram=tomogram)
        else:
            logger.warn("Found unsupported annotation file: %s, %s. Skipping.", f.shape_type, f.format)


def _read_points_annotation_file(anno_file: AnnotationFile, *, anno: Annotation, tomogram: Optional[Tomogram]) -> FullLayerData:
    assert anno_file.shape_type in ("Point", "OrientedPoint")
    assert anno_file.format == "ndjson"
    data, attributes, layer_type = read_points_annotations_ndjson(anno_file.https_path)
    name = anno.object_name
    if tomogram is None:
        attributes["name"] = name
    else:
        attributes["name"] = f"{tomogram.name}-{name}"
    attributes["metadata"] = anno_file.to_dict()
    attributes["face_color"] = _annotation_color(anno)
    return data, attributes, layer_type


def _read_labels_annotation_file(anno_file: AnnotationFile, *, anno: Annotation, tomogram: Optional[Tomogram]) -> FullLayerData:
    assert anno_file.shape_type == "SegmentationMask"
    assert anno_file.format == "zarr"
    data, attributes, _ = read_tomogram_ome_zarr(anno_file.https_path)
    name = anno.object_name
    if tomogram is None:
        attributes["name"] = name
    else:
        attributes["name"] = f"{tomogram.name}-{name}"
    attributes["metadata"] = anno_file.to_dict()
    attributes["opacity"] = 0.5
    attributes["colormap"] = direct_colormap({
        None: np.zeros(4),
        1: _annotation_color(anno),
    })
    return data, attributes, "labels"


def _read_points_data(
    path: str,
) -> List[Tuple[float, float, float]]:
    data: List[Tuple[float, float, float]] = []
    with fsspec.open(path) as f:
        sub_data = [
            _annotation_to_point(annotation)
            for annotation in ndjson.load(f)
            if annotation["type"] in ("point", "orientedPoint")
        ]
        data.extend(sub_data)
    return data


def _annotation_to_point(
    annotation: Dict[str, Any]
) -> Tuple[float, float, float]:
    # Related images are in zyx order, so keep these consistent.
    coords = annotation["location"]
    return (coords["z"], coords["y"], coords["x"])

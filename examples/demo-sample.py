"""Demo that opens napari with sample data opened."""
import logging

import napari
from napari_cryoet_data_portal import logger

logger.setLevel(logging.DEBUG)

viewer = napari.Viewer()
viewer.open_sample(
    plugin="napari-cryoet-data-portal",
    sample="tomogram-10000-ts-026",
)
napari.run()

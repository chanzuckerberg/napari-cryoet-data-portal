"""Demo that opens napari with the data portal widget open."""
import logging

import napari
from napari_cryoet_data_portal import logger

logger.setLevel(logging.INFO)

viewer = napari.Viewer()
viewer.window.add_plugin_dock_widget(plugin_name="napari-cryoet-data-portal")
napari.run()

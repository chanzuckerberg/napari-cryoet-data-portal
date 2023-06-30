"""Demo that opens napari with the data portal widget open."""
import napari

viewer = napari.Viewer()
viewer.window.add_plugin_dock_widget(plugin_name="napari-cryoet-data-portal")
napari.run()

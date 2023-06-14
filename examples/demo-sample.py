"""Demo that opens napari with sample data opened."""
import napari

viewer = napari.Viewer()
viewer.open_sample(
    plugin="napari-cryoet-data-portal",
    sample="tomogram-10000-ts-026",
)
napari.run()

import logging

logger = logging.getLogger("napari_cryoet_data_portal")
# Add our own handler so we can set the level of the logger
# explicitly for easy debugging.
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s : %(name)s : %(levelname)s : %(threadName)s : %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

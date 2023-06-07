from typing import Optional

from qtpy.QtWidgets import (
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QWidget,
)

from napari_cryoet_data_portal._logging import logger


class ControlWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.load = QPushButton("Load")
        self.progress = QProgressBar()
        self.cancel = QPushButton("Cancel")

        self.setLoading(False)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.load)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel)

        self.setLayout(layout)

    def setLoading(self, loading: bool) -> None:
        logger.debug("ControlWidget.setLoading: %s", loading)
        self.load.setEnabled(not loading)
        self.progress.setRange(0, int(not loading))
        self.cancel.setEnabled(loading)

from typing import Callable, Generator, Generic, Optional, TypeVar, Union

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QWidget,
)

from napari_cryoet_data_portal._logging import logger
from napari_cryoet_data_portal._task_worker import TaskWorker

YieldType = TypeVar("YieldType")
SendType = TypeVar("SendType")
ReturnType = TypeVar("ReturnType")
ReturnCallback = Callable[[ReturnType], None]
YieldCallback = Callable[[YieldType], None]
WorkType = Union[
    Callable[..., ReturnType], Generator[YieldType, SendType, ReturnType]
]


class ProgressWidget(QWidget, Generic[YieldType, SendType, ReturnType]):
    """Shows progress and handles cancellation of a task."""

    finished = Signal()

    def __init__(
        self,
        *,
        work: WorkType,
        yieldCallback: Optional[YieldCallback] = None,
        returnCallback: Optional[ReturnCallback] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self._worker: Optional[TaskWorker] = None
        self._work: WorkType = work
        self._yieldCallback: Optional[YieldCallback] = yieldCallback
        self._returnCallback: Optional[ReturnCallback] = returnCallback

        self._last_id: Optional[int] = None

        self.status = QLabel("")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.cancel_button = QPushButton("Cancel")

        self.cancel_button.clicked.connect(self.cancel)

        self._setLoaded()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def submit(self, *args, **kwargs) -> None:
        logger.debug("ProgressWidget.submit: %s", self)
        self.cancel()
        self._worker = TaskWorker(self, self._work, *args, **kwargs)
        self._last_id = self._worker.task_id()
        self._worker.yielded.connect(self._onWorkerYielded)
        self._worker.returned.connect(self._onWorkerReturned)
        self._worker.finished.connect(self._onWorkerFinished)
        self._setLoading()
        self._worker.start()

    def cancel(self) -> None:
        logger.debug("ProgressWidget.cancel: %s", self._worker)
        if self._worker is None:
            return
        self._setCancelling()
        self._worker.cancel()
        self._worker = None

    def _onWorkerYielded(self, task_id: int, value: YieldType) -> None:
        logger.debug("ProgressWidget._onWorkerYielded: %s, %s", task_id, value)
        if self._isTaskCancelled(task_id):
            return
        if self._yieldCallback:
            self._yieldCallback(value)

    def _onWorkerReturned(self, task_id: int, value: ReturnType) -> None:
        logger.debug(
            "ProgressWidget._onWorkerReturned: %s, %s", task_id, value
        )
        if self._isTaskCancelled(task_id):
            return
        if self._returnCallback:
            self._returnCallback(value)
        self._setLoaded()

    def _onWorkerFinished(self, task_id: int) -> None:
        logger.debug("ProgressWidget._onWorkerFinished: %s", task_id)
        # This handles the case when a task was cancelled, but no other
        # tasks were started.
        if self._last_id == task_id:
            self._worker = None
            self._setLoaded()
        self.finished.emit()

    def _isTaskCancelled(self, task_id: int) -> bool:
        if self._worker is None:
            return True
        return self._worker.task_id() != task_id

    def _setLoaded(self) -> None:
        logger.debug("ProgressWidget.setLoaded: %s", self)
        self.hide()

    def _setLoading(self) -> None:
        logger.debug("ProgressWidget.setLoading: %s", self)
        self.status.setText("Loading")
        self.cancel_button.setEnabled(True)
        self.show()

    def _setCancelling(self) -> None:
        logger.debug("ProgressWidget.setCancelling: %s", self)
        self.status.setText("Cancelling")
        self.cancel_button.setEnabled(False)
        self.show()

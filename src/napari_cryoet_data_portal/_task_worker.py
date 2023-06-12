from itertools import count
from typing import Callable, Generator, Generic, TypeVar, Union

from qtpy.QtCore import QObject, Signal
from superqt.utils import GeneratorWorker, WorkerBase, create_worker

ReturnType = TypeVar("ReturnType")
SendType = TypeVar("SendType")
YieldType = TypeVar("YieldType")
WorkType = Union[
    Callable[..., ReturnType], Generator[YieldType, SendType, ReturnType]
]


class TaskWorker(QObject, Generic[YieldType, SendType, ReturnType]):
    """Adds a unique numeric ID to a superqt worker and its signals."""

    yielded = Signal(int, object)
    returned = Signal(int, object)
    finished = Signal(int)
    _id_generator = count()

    def __init__(self, parent: QObject, work: WorkType, *args, **kwargs):
        super().__init__(parent)

        self._id: int = next(TaskWorker._id_generator)
        self._worker: WorkerBase = create_worker(work, *args, **kwargs)
        if isinstance(self._worker, GeneratorWorker):
            self._worker.yielded.connect(self._onWorkerYielded)
        self._worker.returned.connect(self._onWorkerReturned)
        self._worker.finished.connect(self._onWorkerFinished)

    def task_id(self) -> int:
        return self._id

    def start(self) -> None:
        self._worker.start()

    def cancel(self) -> None:
        self._worker.quit()

    def _onWorkerYielded(self, result: YieldType) -> None:
        self.yielded.emit(self._id, result)

    def _onWorkerReturned(self, result: ReturnType) -> None:
        self.returned.emit(self._id, result)

    def _onWorkerFinished(self) -> None:
        self.finished.emit(self._id)

import threading
from queue import Empty
from typing import Callable


class GovernanceBus:
    """
    Event bus between runtime, epistemic, Vault, and Stumpy processes.
    """

    def __init__(self, event_queue, violation_queue) -> None:
        self._event_queue = event_queue
        self._violation_queue = violation_queue
        self._running = False
        self._thread: threading.Thread | None = None
        self._handlers: dict[str, Callable[[dict], None]] = {}

    def register_handler(self, event_type: str, handler: Callable[[dict], None]) -> None:
        self._handlers[event_type] = handler

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="StumpyGovernanceBus")
        self._thread.daemon = True
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        while self._running:
            try:
                event = self._event_queue.get(timeout=0.5)
            except Empty:
                continue

            etype = event.get("type")
            handler = self._handlers.get(etype)

            if handler:
                handler(event)
            else:
                self._violation_queue.put({
                    "type": "unhandled_event",
                    "event": event,
                })

from typing import Protocol, TypeVar

EventT = TypeVar("EventT")


class EventObserver(Protocol[EventT]):
    async def update(self, event: EventT) -> None: ...


class AsyncEventPublisher:
    """Subject observable que notifica secuencialmente a sus observers async."""

    def __init__(self) -> None:
        self._observers: list[EventObserver] = []

    def attach(self, observer: EventObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: EventObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify(self, event) -> None:
        for observer in tuple(self._observers):
            await observer.update(event)

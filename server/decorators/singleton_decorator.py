from typing import Any, Mapping, Type, TypeVar

T = TypeVar("T")


def singleton(cls: Type[T]) -> Type[T]:
    original_new = cls.__new__
    instance: T | None = None

    def __new__(cls_: Type[T], *args: object, **kwargs: Mapping[str, Any]) -> T:
        nonlocal instance
        if instance is None:
            instance = original_new(cls_, *args, **kwargs)
            if hasattr(instance, "__init__"):
                instance.__init__(*args, **kwargs)  # type: ignore
        return instance

    cls.__new__ = __new__  # type: ignore
    return cls

# server/decorators/singleton_decorator.py
from functools import wraps


def singleton(cls):
    """
    Decorador singleton que preserva los hints de tipo y la documentación.
    """
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper

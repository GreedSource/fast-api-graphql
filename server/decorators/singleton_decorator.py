def singleton(cls):
    instances = {}

    class Wrapper(cls):
        def __new__(cls_, *args, **kwargs):
            if cls not in instances:
                instances[cls] = super().__new__(cls_)
            return instances[cls]

    return Wrapper

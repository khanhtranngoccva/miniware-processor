class Definition:
    def __init__(self, func, name: str, tag: str):
        self._name = name
        self._tag = tag
        self._func = func

    @property
    def name(self):
        return self._name

    @property
    def tag(self):
        return self._tag

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


def definition(definition_name, definition_tag):
    def decorator(func):
        return Definition(func, definition_name, definition_tag)

    return decorator
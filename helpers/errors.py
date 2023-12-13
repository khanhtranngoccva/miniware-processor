class HTTPError(Exception):
    def __init__(self, code=500, message="Unspecified server error."):
        self.code = code,
        self.message = message,


class FileInputError(HTTPError):
    def __init__(self, message="Input file(s) is/are invalid."):
        super().__init__(400, message)


class NotFoundError(HTTPError):
    def __init__(self, message="Resource not found."):
        super().__init__(404, message)


class ResourceNotReadyError(HTTPError):
    def __init__(self, message="Resource is currently being processed and is not ready yet."):
        super().__init__(409, message)

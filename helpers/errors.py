class HTTPError(Exception):
    def __init__(self, code=500, message="Unspecified server error."):
        self.code = code,
        self.message = message,


class FileInputError(HTTPError):
    def __init__(self, message="Input file(s) is/are invalid."):
        super().__init__(400, message)

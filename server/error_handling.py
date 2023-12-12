import traceback
from helpers import errors
from flask import Flask


def add_error_handling(app: Flask):
    @app.errorhandler(errors.HTTPError)
    def custom_error_handling(error: errors.HTTPError):
        return (
            {
                "success": False,
                "reason": error.message
            },
            error.code
        )

    @app.errorhandler(Exception)
    def error_handling(error: Exception):
        traceback.print_exception(error)
        return (
            {
                "success": False,
                "reason": "Unspecified error"
            },
            500
        )

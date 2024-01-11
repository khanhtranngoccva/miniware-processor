import flask
from server import database
from server.entity import analysis
from server.entity import file
from server.response import response


def routes(app: flask.Flask):
    @app.get("/analysis/<analysis_id>")
    def get_analysis(analysis_id: str):
        _analysis_id = int(analysis_id)

        with database.db_connect() as conn:
            result = analysis.get_complete_analysis(conn, _analysis_id)

        return response(result)

    @app.get("/analysis/<analysis_id>/download_file")
    def download_file(analysis_id: str):
        _analysis_id = int(analysis_id)

        with database.db_connect() as conn:
            obj = analysis.get_analysis(conn, _analysis_id)
            result = file.get_download_url(conn, obj["file_id"])

        return response(result)

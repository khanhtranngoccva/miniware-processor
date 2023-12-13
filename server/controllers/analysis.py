import flask
from server import database
from server.entity import analysis
from server.response import response


def routes(app: flask.Flask):
    @app.get("/analysis/<analysis_id>")
    def get_analysis(analysis_id: str):
        _analysis_id = int(analysis_id)

        with database.db_connect() as conn:
            result = analysis.get_complete_analysis(conn, _analysis_id)

        return response(result)

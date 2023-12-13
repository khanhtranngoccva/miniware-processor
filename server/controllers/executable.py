import os
import uuid

import flask
from flask import request
import helpers.directory
from server.response import response
import server.entity.file
import server.entity.analysis
from server.database import db_connect


def routes(app: flask.Flask):
    @app.post("/upload")
    def upload_executable():
        executable = request.files["file"]

        temp_name = uuid.uuid4().hex
        temp_path = helpers.directory.get_temp_path(f"executable/{temp_name}")
        filename = executable.filename

        executable.save(temp_path)
        # Multiple connection representing multiple commit-able stages.
        with db_connect() as conn:
            file_id = server.entity.file.create_file(conn, temp_path)

        with db_connect() as conn:
            analysis_id = server.entity.analysis.create_analysis(conn, file_id, filename)
            # Should run in their own thread because it might take longer than what is allowed within 2 minutes.
            server.entity.analysis.initiate_analysis(conn, analysis_id, temp_path)

        try:
            os.remove(temp_path)
        except (FileNotFoundError, PermissionError):
            pass

        return response({
            # Replace this field with the ID given from the database.
            "id": analysis_id,
            "filename": executable.filename,
        })

    @app.post("/analyze-from-hash")
    def analyze_from_hash():
        params = request.json
        hash_algorithm = params["algorithm"]
        hash_value = params["value"]

        # Make a PostgresSQL query here to retrieve the file ID/one of the unique hash in the Hash relation, then
        # download the file from whatever cloud storage.

        # We can either use sha256 as unique identifier on the cloud (which is better than local IDs in my opinion since
        # it is deterministic).

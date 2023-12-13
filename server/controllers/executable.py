import os
import uuid

import flask
from flask import request
import helpers.directory
from server.response import response
import server.entity.file


def routes(app: flask.Flask):
    @app.post("/upload")
    def upload_executable():
        executable = request.files["file"]

        temp_name = uuid.uuid4().hex
        temp_path = helpers.directory.get_temp_path(f"executable/{temp_name}")

        executable.save(temp_path)
        server.entity.file.create_file(temp_path)

        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass

        # Create an analysis object here and store it in the database.
        # An analysis object has 3 attributes:
        #   - A file FK linking to the file
        #   - A unique ID.
        #   - A filename (since a file can be analyzed multiple times under different names)
        #   - A state flag (PROCESSING, COMPLETE)

        # Any information relations that belong to the analysis object will have a FK named "analysis_id" linked back
        # to the analysis object.
        return response({
            # Replace this field with the ID given from the database.
            "id": uuid.uuid4().hex,
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

from flask import Flask
from flask_cors import CORS
from server import env

app = Flask("miniware_processor")
CORS(app)

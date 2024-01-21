import json
import subprocess
from helpers.directory import get_application_path


def analyze_file(path):
    command = [
        get_application_path("/tools/capa/capa"),
        "-j",
        path,
    ]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
    output, error = proc.communicate()

    return json.loads(output.rstrip("[0m\n\r"))

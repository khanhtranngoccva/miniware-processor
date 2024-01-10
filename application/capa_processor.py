import json
import subprocess
from helpers.directory import get_application_path


def analyze_file(path):
    command = [
        get_application_path("/tools/capa/windows/capa.exe"),
        path,
        "-j"
    ]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, text=True, shell=True)
    output, error = proc.communicate()
    return json.loads(output.rstrip("[0m\n\r"))

import subprocess
import json
from helpers.directory import get_application_path

command = [
    get_application_path("./tools/capa/windows/capa.exe"),
    get_application_path("./test_coccoc.exe"),
    "-j",
]

try:
    print("capa output:")

    proc = subprocess.Popen(command, stdout=subprocess.PIPE, text=True, shell=True)
    output, error = proc.communicate()

    with open("data_function.json", "w") as file:
        file.write(output)

    print(json.loads(output.rstrip("[0m\n\r")))

except Exception as e:
    print(f"Error: {e}")

from pathlib import Path
import os
from constants import ROOT_DIRECTORY


def get_temp_path(path: str):
    temp_directory = os.path.join(ROOT_DIRECTORY, "temp")
    output = Path(temp_directory).joinpath(path.lstrip("/\\")).resolve()
    output.relative_to(Path(temp_directory).resolve())
    return output


os.makedirs(get_temp_path("/executable"), exist_ok=True)


if __name__ == '__main__':
    print(get_temp_path("/oof//o/"))

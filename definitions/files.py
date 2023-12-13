import re
from helpers.definition_helper import definition


@definition("Windows absolute paths", "File")
def windows_absolute_file_path(raw_string: str):
    res = []
    regex = re.compile(
        r'(^|)'
        r'([a-zA-Z]:|\\\\[^\/\\:*?"\'<>|]+[\\/]+[^\/\\:*?"\'<>|]+)([\\/]+[^\/\\:*?"\'<>|]+)+(\.[^\/\\:*?"\'<>|]+)'
        r'(?=[\s"\',:;<>]|$)',
        re.IGNORECASE)
    for entry in regex.finditer(raw_string):
        res.append([entry.start(), entry.end()])
    return res


@definition("Filename", "File")
def filename(raw_string: str):
    res = []
    regex = re.compile(
        r'(^|[\s\W])'
        r'('
        r'[\w^\/\\:*?"<>|,\']+'
        r'(\.[\w^\/\\:*?"<>|,\']+)'
        r')'
        r'(?=[\s\W]|$)',
        re.IGNORECASE)
    for entry in regex.finditer(raw_string):
        res.append([entry.start(), entry.end()])
    return res


if __name__ == '__main__':
    print(windows_absolute_file_path("C:/Windows/coccoc.exe','C:/data.c'"))

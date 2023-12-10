import re
from definition_helper import definition


@definition("Windows absolute paths", "File")
def windows_absolute_file_path(raw_string: str):
    res = []
    regex = re.compile(
        r'(^|)'
        r'^([a-zA-Z]:|\\\\[^\/\\:*?"<>|]+[\\/]+[^\/\\:*?"<>|]+)([\\/]+[^\/\\:*?"<>|]+)+(\.[^\/\\:*?"<>|]+)$'
        r'(?=[\s"\',:;<>]|$)',
        re.IGNORECASE)
    for entry in regex.findall(raw_string):
        res.append(entry[1])
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
    for entry in regex.findall(raw_string):
        res.append(entry[1])
    return res


if __name__ == '__main__':
    print(filename("coccoc.exe','data.c'"))

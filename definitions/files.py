import re
from definition_helper import definition


@definition("Windows absolute paths on disk", "File")
def windows_absolute_file_path(raw_string: str):
    res = []
    regex = re.compile(
        r'(^|)'
        r'(([a-zA-Z]\:|\\\\[^\/\\:*?"<>|,]+[\\/]+[^\/\\:*?"<>|,]+)'
        r'([\\/]+[^\/\\:*?"<>|,]+)+'
        r'(\.[^\/\\:*?"<>|,]+)?)'
        r'(?=[\s\W]|$)',
        re.IGNORECASE)
    for entry in regex.findall(raw_string):
        res.append(entry[1])
    return res


if __name__ == '__main__':
    print(windows_absolute_file_path("C:\\.vscode\\data.exe3-2_C:/dataset"))

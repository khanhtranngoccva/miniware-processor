import re

from helpers.definition_helper import definition


@definition("Detects HTTP and HTTPS URLs", "Internet")
def http_url(raw_string):
    result = []
    regex1 = re.compile(
        r"(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}"
        r"\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*))(?=[\s\W]|$)",
        re.IGNORECASE)
    matches = [*regex1.finditer(raw_string)]
    for entry in matches:
        result.append([entry.start(), entry.end()])
    return result


@definition("Detects domain names", "Internet")
def domain_name(raw_string):
    result = []
    regex1 = re.compile(r"^((?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6})(?=[\s\W]|$)", re.IGNORECASE)
    regex2 = re.compile(r"(?<=[\s\W])((?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6})(?=[\s\W]|$)",
                        re.IGNORECASE)

    matches = [*regex1.finditer(raw_string), *regex2.finditer(raw_string)]
    for entry in matches:
        result.append([entry.start(), entry.end()])
    return result


@definition("IP Address", "Internet")
def ip_address(raw_string: str):
    result_ips = []

    regex1 = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?=[\s\W]|$)", re.IGNORECASE)
    regex2 = re.compile(r"(?<=[\s\W])(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?=[\s\W]|$)", re.IGNORECASE)

    matches = [*regex1.finditer(raw_string), *regex2.finditer(raw_string)]

    for match in matches:
        if is_valid_ip(match.group()):
            result_ips.append([match.start(), match.end()])

    return result_ips


def is_valid_ip(ip: str):
    tok = ip.split(".")
    if len(tok) != 4:
        return False
    for str_val in tok:
        try:
            int_val = int(str_val)
            if not 0 <= int_val <= 255:
                return False
        except ValueError:
            return False
    return True


if __name__ == '__main__':
    print(http_url("https://google.com, 1, 2, 3http://vnexpress.net"))
    print(domain_name("https://google.com, 1, 2, 3http://vnexpress.net"))
    print(ip_address("192.168.2.1,https://google.com, 1, 2, 3http://vnexpress.net, 192.168.5.1"))

import re

from definition_helper import definition


@definition("Detects HTTP and HTTPS URLs", "Internet")
def http_url(raw_string):
    result = []
    regex = re.compile(
        r"(^|[\s\W])(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}"
        r"\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*))(?=[\s\W]|$)",
        re.IGNORECASE)
    matches = regex.findall(raw_string)
    for entry in matches:
        result.append(entry[1])
    return result


@definition("IP Address", "Internet")
def ip_address(raw_string: str):
    import helpers.misc
    result_ips = []

    regex = re.compile(r"(^|[\s\W])(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?=[\s\W]|$)", re.IGNORECASE)
    cur_match = regex.findall(raw_string)

    for _, match in cur_match:
        if helpers.misc.is_valid_ip(match):
            result_ips.append(match)

    return result_ips



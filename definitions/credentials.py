import re

from definition_helper import definition


@definition("Detects email addresses", "Credentials")
def email_address(raw_string: str):
    regex = re.compile(r"(^|[\s\W])([\w\-.]+@([\w\-]+\.)+[a-z]{2,4})(?=[\s\W\d]|$)", re.IGNORECASE)
    result_emails = []

    cur_match = regex.findall(raw_string)
    for entry in cur_match:
        result_emails.append(entry[1])

    return result_emails

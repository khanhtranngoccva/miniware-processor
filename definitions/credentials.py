import re

from helpers.definition_helper import definition


@definition("Detects email addresses", "Credentials")
def email_address(raw_string: str):
    regex = re.compile(r"(^|[\s\W])([\w\-.]+@([\w\-]+\.)+[a-z]{2,4})(?=[\s\W\d]|$)", re.IGNORECASE)
    result_emails = []

    cur_match = regex.finditer(raw_string)
    for entry in cur_match:
        result_emails.append([entry.start(), entry.end()])
    return result_emails

def dont_include_this():
    pass

if __name__ == '__main__':
    print("1")
    print(email_address("khanhtranngoccva@gmail.com, 1, 3, 4"))

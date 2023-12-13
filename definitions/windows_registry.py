from helpers.definition_helper import definition

REGISTRY_SIGNATURE_LIST = [
    "HKEY_LOCAL_MACHINE",
    "HKEY_CURRENT_CONFIG",
    "HKEY_CLASSES_ROOT",
    "HKEY_CURRENT_USER",
    "HKEY_USERS",
    "HKEY_PERFORMANCE_DATA",
    "HKEY_DYN_DATA",
    "HKLM",
    "HKCC",
    "HKCU",
    "HKU",
]
_REGISTRY_KEY_LIST = map(lambda x: x.lower(), REGISTRY_SIGNATURE_LIST)


@definition("Windows registry keywords", "Registry")
def registry(raw_string: str):
    res = []

    lowercase_string = raw_string.lower()
    for key in REGISTRY_SIGNATURE_LIST:
        try:
            idx = lowercase_string.index(key)
            res.append([idx, idx + len(key)])
        except ValueError:
            continue
    return res

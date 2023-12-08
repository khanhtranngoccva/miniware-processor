import re
from definition_helper import definition


@definition("Detects HTTP and HTTPS URLs", "Internet")
def http_url(raw_string):
    regex = re.compile("^.*https?://.*$", re.IGNORECASE)
    return bool(regex.match(raw_string))


CRYPTOCURRENCY_LIST = [
    "Monero",
    "Bitcoin",
    "Ethereum",
    "Solana",
    "USDt",
    "BNB",
    "XRP",
    "USDC",
    "Cardano",
    "Dogecoin",
    "Avalanche",
    "TRON",
    "Chainlink",
    "Polkadot",
    "Polygon",
    "Toncoin",
    "Shiba Inu",
    "Litecoin",
    "Dai",
    "Bitcoin Cash",
]
_CRYPTOCURRENCY_LIST = map(lambda x: x.lower(), CRYPTOCURRENCY_LIST)


@definition("Detects cryptocurrency sites", "Cryptocurrency")
def cryptocurrency(raw_string: str):
    lowercase_string = raw_string.lower()
    for currency in _CRYPTOCURRENCY_LIST:
        try:
            lowercase_string.index(currency)
            return True
        except ValueError:
            continue
    return False


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
    lowercase_string = raw_string.lower()
    for key in REGISTRY_SIGNATURE_LIST:
        try:
            lowercase_string.index(key)
            return True
        except ValueError:
            continue
    return False


@definition("File extensions", "File")
def extensions(raw_string: str):
    regex = re.compile(r"^[a-z0-9_-]*\.[a-z]{3}$", re.IGNORECASE)
    return bool(regex.match(raw_string))


@definition("Detects email addresses", "Email")
def email_address(raw_string: str):
    regex = re.compile(r"^.*[\w\-.]+@([\w-]+\.)+[\w-]{2,4}.*$", re.IGNORECASE)
    return bool(regex.match(raw_string))


if __name__ == '__main__':
    url = "https://google.com?data=monero"
    print(http_url(url))
    print(cryptocurrency(url))

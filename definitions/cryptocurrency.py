from helpers.definition_helper import definition

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


@definition("Detects cryptocurrencies", "Cryptocurrency")
def cryptocurrency(raw_string: str):
    res = []
    lowercase_string = raw_string.lower()
    for currency in _CRYPTOCURRENCY_LIST:
        try:
            idx = lowercase_string.index(currency)
            res.append(raw_string[idx:idx + len(currency)])
        except ValueError:
            continue
    return res


if __name__ == '__main__':
    print(cryptocurrency("Monero, BiTcoin"))

from Scraper.scraper import Scraper


cex = {
    "coinbase": "coinbase-exchange",
}


def build_dex_endpoint(dex: str, version: str = None, network: str = None):
    endpoint = dex.lower()

    if version != None:
        endpoint = f"{endpoint}-{version.lower()}"

    if network != None:
        endpoint = f"{endpoint}-{network}"

    return endpoint


exchange_mapping = {
    1: "binance-us",
    2: "binance",
    3: "bitmart",
    4: "coinbase-exchange",
    5: "kraken",
    6: "kucoin",
    7: "mexc",
    8: "okx",
    9: "tradeogre",
}


def scrape_many_cex(exchanges: list):

    for e in exchanges:
        s = Scraper(e, exchange_type="CEX")
        s.scrape_tickers()
        df = s.scraped_data
        df.to_csv(s.file_path)
        s.sort_files()


def scrape_cex():

    exchange = "gemini"
    s = Scraper(exchange, exchange_type="CEX")
    s.scrape_tickers()
    df = s.scraped_data
    df.to_csv(s.file_path)
    s.sort_files()


def scrape_dex():

    network = "polygon"
    d = build_dex_endpoint("uniswap", "v3", network.lower())

    exchange = d
    s = Scraper(exchange, exchange_type="DEX", network=network.lower())

    s.scrape_tickers()

    df = s.scraped_data

    df.to_csv(s.file_path)

    s.sort_files()


if __name__ == "__main__":
    scrape_many_cex(list(exchange_mapping.values()))
    # scrape_cex()

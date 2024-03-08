import os

import time

import pandas as pd

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Get the current working directory.
cwd = os.getcwd()

# Selenium browser settings
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")


class Scraper:
    def __init__(self, exchange: str, exchange_type: str = "CEX", network=None) -> None:

        self.exchange_type = exchange_type.upper()
        # When the url does not match the filename.
        self.edge_cases = {
            "cases": ["coinbase-exchange"],
            "coinbase-exchange": "coinbase",
        }

        # Logic to determine if an edge case.
        if exchange.lower() in self.edge_cases["cases"]:
            self.exchange_name = self.edge_cases[exchange.lower()]
        else:
            self.exchange_name = exchange.lower()

        print(f"Exchange: {self.exchange_name}")
        self.url = "https://coinmarketcap.com/exchanges/{}/".format(exchange.lower())
        self.file_path = (
            f"SupportedCoins\\{self.exchange_type}\\{self.exchange_name}.csv"
        )
        self.chrome_driver = "D:\\Chromedriver\\chromedriver.exe"
        self.browser = None
        self.scraped_data = pd.DataFrame()

    """----------------------------------- Browser Utilities -----------------------------------"""

    def create_browser(self, url=None):
        """
        :param url: The website to visit.
        :return: None
        """
        service = Service(executable_path=self.chrome_driver)
        self.browser = webdriver.Chrome(service=service, options=chrome_options)
        # Default browser route
        if url == None:
            self.browser.get(url=self.url)
        # External browser route
        else:
            self.browser.get(url=url)

    """-----------------------------------"""

    def read_data(self, xpath: str, wait: bool = False, wait_time: int = 5) -> str:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: (str) Text of the element.
        """

        if wait:
            data = WebDriverWait(self.browser, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        else:
            data = self.browser.find_element("xpath", xpath)
        # Return the text of the element found.
        return data.text

    """-------------------------------"""

    def click_button(self, xpath: str, wait: bool = False, wait_time: int = 5) -> None:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: None. Because this function clicks the button but does not return any information about the button or any related web elements.
        """

        if wait:
            element = WebDriverWait(self.browser, wait_time).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        else:
            element = self.browser.find_element("xpath", xpath)
        element.click()

    """-------------------------------"""

    def scrape_tickers(self, div: int = 4):
        if self.browser == None:
            self.create_browser()
        pair_row = 1
        name_row = 1

        xpaths = {
            "CEX": {
                "pair_xpath": "/html/body/div[1]/div[2]/div/div[2]/div/div[{}]/div[1]/div/table/tbody/tr[{}]/td[3]/div/a[1]",
                "name_xpath": "/html/body/div[1]/div[2]/div/div[2]/div/div[{}]/div[1]/div/table/tbody/tr[{}]/td[2]/a/div/div/p",
                "load_more_xpath": "/html/body/div[1]/div[2]/div/div[2]/div/div[{}]/div[3]/button",
            },
            "DEX": {
                "pair_xpath": "/html/body/div[1]/div[2]/div/div[2]/div/div[{}]/div[1]/div/table/tbody/tr[{}]/td[3]/a",
                "name_xpath": "/html/body/div[1]/div[2]/div/div[2]/div/div[{}]/div[1]/div/table/tbody/tr[{}]/td[2]/a/div/div/p",
                "load_more_xpath": "/html/body/div[1]/div[2]/div/div[2]/div/div[{}]/div[3]/button",
            },
        }

        pair_xpath = xpaths[self.exchange_type]["pair_xpath"]
        name_xpath = xpaths[self.exchange_type]["name_xpath"]
        button_xpath = xpaths[self.exchange_type]["load_more_xpath"]

        scraping = True
        supported_coins = []
        index = 0
        if self.exchange_type == "CEX":
            scroll_control = 40

        else:
            scroll_control = 50

        while scraping:

            try:
                # Runs every X indexes.
                if (index + 1) % scroll_control == 0:
                    self.browser.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    time.sleep(2)

                pair = self.read_data(
                    pair_xpath.format(div, pair_row),
                    wait=True,
                )
                base = pair.split("/")[0]
                print(f"[{base}]")
                name = self.read_data(
                    name_xpath.format(div, name_row),
                    wait=True,
                )
                data = {"name": name, "base": base, "pair": pair}
                supported_coins.append(data)
                pair_row += 1
                name_row += 1
                index += 1
            except TimeoutException:

                # scraping = False
                try:
                    # Click load more button to populate page with new elements.
                    try:
                        self.click_button(button_xpath.format(div))

                    except Exception as e:
                        print(f"Error1: {e}")
                        try:
                            self.click_button(button_xpath.format(4))
                        except Exception as e:
                            print(f"Error2: {e}")
                    # After loading more elements, try to scrape where it left off before the error.
                    pair = self.read_data(
                        pair_xpath.format(div, pair_row),
                        wait=True,
                    )
                    base = pair.split("/")[0]
                    print(f"Alt: [{base}]")
                    name = self.read_data(
                        name_xpath.format(div, name_row),
                        wait=True,
                    )
                    data = {"name": name, "base": base, "pair": pair}
                    supported_coins.append(data)
                    pair_row += 1
                    name_row += 1
                    index += 1
                # If element is still not found after loading more, then end the scraping.
                except Exception as e:
                    print(f"Exception1: {e}")
                    scraping = False

        print(f"Data: {supported_coins}")

        self.scraped_data = pd.DataFrame(supported_coins)
        if self.scraped_data.empty:
            # Try alternate xpaths
            self.scrape_tickers(div=3)

    def sort_files(self):
        df = pd.read_csv(self.file_path)
        try:
            df = df.set_index("Unnamed: 0")
        except KeyError:
            pass
        # Convert tickers to uppercase to make sorting easier.
        df["base"] = df["base"].str.upper()
        df = df.sort_values(by="base")
        df = df.set_index("pair")
        # df = df.drop_duplicates()
        df.to_csv(self.file_path)

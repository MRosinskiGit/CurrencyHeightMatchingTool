import os

import requests
from loguru import logger
from requests.status_codes import codes as ResponseCode

from FunfactsHandler import Facts
from data.countries import currency_codes


class CurrencyReader:
    def __init__(self, api_key, base_currency: str):
        logger.info("Creating CurrencyReader object.")
        self.__base_currency = base_currency
        self.currencies_data_base = None
        self.real_currencies_recalculated = None
        self.crypto_currencies_recalculated = None
        self.__BASE_URL = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}"
        self.Deepseek = Facts(os.getenv("DEEPSEEK_API"))

        self.download_currency_data()
        # Todo Remove below - only for limiting api usage
        # with open(r"tests/test_data/response_data.json") as f:
        #     self.currencies_data_base = json.load(f)
        #     self.__recalculate_base(self.__base_currency)

        if self.currencies_data_base is None:
            raise ValueError("No currency data available.")

    @property
    def base_currency(self):
        return self.__base_currency

    @base_currency.setter
    def base_currency(self, new_currency):
        logger.info(f"Changing base currency to {new_currency}")
        if self.currencies_data_base.get("rates").get(new_currency) is None:
            logger.critical(f"Provided symbol name {new_currency} not found.")
            raise ValueError("Currency symbol not found in database.")
        logger.success("Base currency modified.")
        self.__base_currency = new_currency
        self.__recalculate_base(self.__base_currency)

    def download_currency_data(self):
        logger.info("Downloading currencies info.")
        api_request = requests.get(self.__BASE_URL)
        if api_request.status_code != ResponseCode["ok"]:
            logger.critical(f"Connection error with code {api_request.status_code}.")
            raise ConnectionError(f"API response status code: {api_request.status_code}.")
        logger.success("Currencies data updated correctly.")
        self.currencies_data_base = api_request.json()
        logger.trace(self.currencies_data_base)
        self.__recalculate_base(self.__base_currency)

    def __recalculate_base(self, base):
        logger.info(f"Recalculating all currency rates to {base} currency.")
        rates = self.currencies_data_base.get("rates")
        counties_currency_codes = [symbol for country, symbol in currency_codes.items()]
        if base == self.currencies_data_base.get("base"):
            logger.success("No recalculation needed.")
            self.real_currencies_recalculated = {
                key: float(value) for key, value in rates.items() if key in counties_currency_codes
            }
            self.crypto_currencies_recalculated = {
                key: float(value) for key, value in rates.items() if key not in counties_currency_codes
            }
            return

        base_rate = rates.get(base)
        if base_rate is None:
            logger.warning(f"Currency {base} not found in database. Calculation interrupted.")
            return None

        self.real_currencies_recalculated = {
            key: float(value) / float(base_rate) for key, value in rates.items() if key in counties_currency_codes
        }
        self.crypto_currencies_recalculated = {
            key: float(value) / float(base_rate) for key, value in rates.items() if key not in counties_currency_codes
        }
        logger.success("Recalculation successfully.")

    def find_closest_currency(self, height):
        logger.info("Matching global Currency that matches user's height.")
        currency_symbol = min(
            self.real_currencies_recalculated,
            key=lambda curr: abs(height - self.real_currencies_recalculated.get(curr)),
        )
        logger.success(
            f"Currency matched: {currency_symbol} with ratio {self.real_currencies_recalculated[currency_symbol]}"
        )
        return currency_symbol

    def find_closest_crypto(self, height):
        logger.info("Matching crypto that matches user's height.")
        crypto_symbol = min(
            self.crypto_currencies_recalculated,
            key=lambda curr: abs(height - self.crypto_currencies_recalculated.get(curr)),
        )
        logger.success(
            f"Crypto matched: {crypto_symbol} with ratio: {self.crypto_currencies_recalculated[crypto_symbol]}"
        )
        return crypto_symbol

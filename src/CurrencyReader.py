import requests
from requests.status_codes import codes as ResponseCode
from loguru import logger

from data.countries import currency_codes


class CurrencyReader:
    def __init__(self, api_key, base_currency: str):
        logger.info("Creating CurrencyReader object.")
        self.base_currency = base_currency
        self.currencies_data_base = None
        self.real_currencies_recalculated = None
        self.crypto_currencied_recalculated = None
        self.__BASE_URL = (
            f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}"
        )

        self.update_currencies_data()
        if self.currencies_data_base is None:
            raise ValueError("No currency data available.")
        self.recalculate_base(self.base_currency)

    def update_currencies_data(self):
        logger.info("Updating currencies info.")
        api_request = requests.get(self.__BASE_URL)
        if api_request.status_code != ResponseCode["ok"]:
            logger.critical(f"Connection error with code {api_request.status_code}.")
            raise ConnectionError(
                f"API response status code: {api_request.status_code}."
            )
        logger.success("Currencies data updated correctly.")
        self.currencies_data_base = api_request.json()
        logger.trace(self.currencies_data_base)

    def recalculate_base(self, base):
        logger.info(f"Recalculating all currency rates to {base} currency.")
        rates = self.currencies_data_base.get("rates")
        counties_currency_codes = [symbol for country, symbol in currency_codes.items()]
        if base == self.currencies_data_base.get("base"):
            logger.success("No recalculation needed.")
            self.real_currencies_recalculated = {
                key: float(value)
                for key, value in rates.items()
                if key in counties_currency_codes
            }
            self.crypto_currencied_recalculated = {
                key: float(value)
                for key, value in rates.items()
                if key not in counties_currency_codes
            }
            return

        base_rate = rates.get(base)
        if base_rate is None:
            logger.warning(
                f"Currency {base} not found in database. Calculation interrupted."
            )
            return None

        self.real_currencies_recalculated = {
            key: float(value) / float(base_rate)
            for key, value in rates.items()
            if key in counties_currency_codes
        }
        self.crypto_currencied_recalculated = {
            key: float(value) / float(base_rate)
            for key, value in rates.items()
            if key not in counties_currency_codes
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
            self.crypto_currencied_recalculated,
            key=lambda curr: abs(
                height - self.crypto_currencied_recalculated.get(curr)
            ),
        )
        logger.success(
            f"Crypto matched: {crypto_symbol} with ratio: {self.crypto_currencied_recalculated[crypto_symbol]}"
        )
        return crypto_symbol

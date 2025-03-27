import requests
from requests.status_codes import codes as ResponseCode
from loguru import logger


class CurrencyReader:
    def __init__(self, api_key, base_currency: str):
        logger.info("Creating CurrencyReader object.")
        self.base_currency = base_currency
        self.currencies_data_base = None
        self.currencies_recalculated = None
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
        if base == self.currencies_data_base.get("base"):
            logger.success("No recalculation needed.")
            self.currencies_recalculated = {
                key: float(value) for key, value in rates.items()
            }
            return

        base_rate = rates.get(base)
        if base_rate is None:
            logger.warning(
                f"Currency {base} not found in database. Calculation interrupted."
            )
            return None

        self.currencies_recalculated = {
            key: float(value) / float(base_rate) for key, value in rates.items()
        }
        logger.success("Recalculation successfully.")
        logger.trace(self.currencies_recalculated)

    def find_closest_currency(self, height):
        logger.info("Matching global Currency that matches user's height.")
        currency_symbol = min(
            self.currencies_recalculated,
            key=lambda curr: abs(height - self.currencies_recalculated.get(curr)),
        )
        logger.success(f"Currency matched: {currency_symbol}")
        return currency_symbol

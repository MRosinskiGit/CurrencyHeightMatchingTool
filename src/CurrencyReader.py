import os

import requests
from loguru import logger
from requests.status_codes import codes as ResponseCode

from FunfactsHandler import Facts
from data.countries import currency_codes


class CurrencyReader:
    """A class to handle currency data retrieval, conversion, and matching operations.

    This class connects to the CurrencyFreaks API to get current exchange rates,
    allows changing the base currency, and provides methods to find currencies
    closest to a given value.

    Attributes:
        _raw_rates_data (dict): Raw currency data from API.
        real_currencies_recalculated (dict): Real currencies converted to base currency.
        crypto_currencies_recalculated (dict): Crypto currencies converted to base currency.
    """

    def __init__(self, api_key, base_currency: str):
        """Initializes the CurrencyReader with API key and base currency.

        Args:
            api_key (str): API key for CurrencyFreaks service.
            base_currency (str): 3-letter currency code to use as base for conversions.

        Raises:
            ValueError: If currency data cannot be loaded.
        """
        logger.info("Creating CurrencyReader object.")
        self.__base_currency = base_currency
        self._raw_rates_data = None
        self.real_currencies_recalculated = None
        self.crypto_currencies_recalculated = None
        self.__BASE_URL = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}"
        self.Deepseek = Facts(os.getenv("DEEPSEEK_API"))

        self.download_currency_data()

        if self._raw_rates_data is None:
            raise ValueError("No currency data available.")

    @property
    def base_currency(self):
        """str: Gets the current base currency code."""
        return self.__base_currency

    @base_currency.setter
    def base_currency(self, new_currency):
        """Sets a new base currency and recalculates all rates.

        Args:
            new_currency (str): 3-letter currency code to set as new base.

        Raises:
            ValueError: If the currency symbol is not found in database.
        """

        assert isinstance(new_currency, str)
        new_currency = new_currency.upper()
        logger.info(f"Changing base currency to {new_currency}")
        if self._raw_rates_data.get("rates").get(new_currency) is None:
            logger.critical(f"Provided symbol name {new_currency} not found.")
            raise ValueError("Currency symbol not found in database.")
        logger.success("Base currency modified.")
        self.__base_currency = new_currency
        self.__recalculate_base(self.__base_currency)

    @staticmethod
    def validate_currency_symbol(method):
        def wrapper(self, *args, **kwargs):
            all_args = list(args)
            all_args.extend([value for key, value in kwargs.items()])
            if not any([arg in self.__extract_all_currency_symbols() for arg in args]):
                raise ValueError("Currency not found.")
            return method(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_height(method):
        def wrapper(self, *args, **kwargs):
            height = kwargs.get("height") if kwargs.get("height") else list(args)[0]
            assert height is not None, "Height can't be none."
            if isinstance(height, str):
                height = height.replace(",", ".").replace(" ", "")
                height = float(height)
            args = (height,)
            kwargs = {}
            return method(self, *args, **kwargs)

        return wrapper

    def download_currency_data(self):
        """Downloads the latest currency data from API.

        Raises:
            ConnectionError: If API request fails.
        """
        logger.info("Downloading currencies info.")
        api_request = requests.get(self.__BASE_URL)
        if api_request.status_code != ResponseCode["ok"]:
            logger.critical(f"Connection error with code {api_request.status_code}.")
            raise ConnectionError(f"API response status code: {api_request.status_code}.")
        logger.success("Currencies data updated correctly.")
        self._raw_rates_data = api_request.json()
        logger.trace(self._raw_rates_data)
        self.__recalculate_base(self.__base_currency)

    @validate_currency_symbol
    def __recalculate_base(self, base):
        """Recalculates all currency rates relative to the specified base currency.

        Separates real currencies from cryptocurrencies during recalculation.

        Args:
            base (str): The currency code to use as new base for calculations.
        """
        logger.info(f"Recalculating all currency rates to {base} currency.")
        rates = self._raw_rates_data.get("rates")
        counties_currency_codes = [symbol for country, symbol in currency_codes.items()]
        if base == self._raw_rates_data.get("base"):
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

    @validate_height
    def find_closest_currency(self, height):
        """Finds the real currency with exchange rate closest to the given value.

        Args:
            height (float): Value to compare currency rates against.

        Returns:
            str: 3-letter code of the closest currency.
        """
        logger.info("Matching global Currency that matches user's height.")
        currency_symbol = min(
            self.real_currencies_recalculated,
            key=lambda curr: abs(height - self.real_currencies_recalculated.get(curr)),
        )
        logger.success(
            f"Currency matched: {currency_symbol} with ratio {self.real_currencies_recalculated[currency_symbol]}"
        )
        return currency_symbol

    @validate_height
    def find_closest_crypto(self, height):
        """Finds the cryptocurrency with exchange rate closest to the given value.

        Args:
            height (float): Value to compare cryptocurrency rates against.

        Returns:
            str: Symbol of the closest cryptocurrency.
        """
        logger.info("Matching crypto that matches user's height.")
        crypto_symbol = min(
            self.crypto_currencies_recalculated,
            key=lambda curr: abs(height - self.crypto_currencies_recalculated.get(curr)),
        )
        logger.success(
            f"Crypto matched: {crypto_symbol} with ratio: {self.crypto_currencies_recalculated[crypto_symbol]}"
        )
        return crypto_symbol

    def __extract_all_currency_symbols(self) -> list:
        return list(self._raw_rates_data.get("rates").keys())

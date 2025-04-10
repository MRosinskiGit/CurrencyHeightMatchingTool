from pathlib import Path
from loguru import logger
import pytest
from dotenv import load_dotenv
from mock import Mock, patch
import json
from src.CurrencyReader import CurrencyReader

load_dotenv()
logger.configure(handlers={})
FAKE_API = "00000000000000000000000"


@pytest.fixture
def load_json():
    def _load_json(filename):
        path = Path(__file__).parent / "test_data" / filename
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    return _load_json


@pytest.fixture
def api_mock(load_json, status_code=200, response_data_file="response_data.json"):
    api_mock = Mock()
    api_mock.status_code = status_code
    api_mock.json.return_value = load_json(response_data_file)

    with patch("requests.get", return_value=api_mock) as api_yield_mock:
        yield api_yield_mock


@pytest.mark.parametrize("base_currency", ["USD", "PLN", "EUR"])
def test_CurrencyReader_init(api_mock, base_currency):
    Reader = CurrencyReader(FAKE_API, base_currency)
    assert Reader is not None
    assert Reader._raw_rates_data is not None
    assert Reader.real_currencies_recalculated is not None
    assert Reader.crypto_currencies_recalculated is not None


def test_CurrencyReader_init_wrong_api():
    with pytest.raises(ConnectionError):
        CurrencyReader(FAKE_API, "USD")


def test_CurrencyReader_init_incorrect_currency(api_mock):
    with pytest.raises(ValueError):
        CurrencyReader(FAKE_API, "X!X")


class Test_CurrencyReader:
    @pytest.fixture(autouse=True)
    def initialize(self, api_mock):
        self.Reader = CurrencyReader(FAKE_API, "USD")

    @pytest.mark.parametrize("new_currency, expected", [("pln", "PLN"), ("USD", "USD"), ("PLN", "PLN")])
    def test_change_base(self, new_currency, expected):
        self.Reader.base_currency = new_currency
        assert self.Reader.base_currency == expected

    @pytest.mark.parametrize(
        "new_currency, exception", [(None, AssertionError), (1, AssertionError), ("dupa", ValueError), ("", ValueError)]
    )
    def test_change_base_exception(self, new_currency, exception):
        with pytest.raises(exception):
            self.Reader.base_currency = new_currency

    def test_CurrencyReader_USD_recalculation(self):
        recalculate_to_floats = {key: float(value) for key, value in self.Reader._raw_rates_data["rates"].items()}
        all_rates = {}
        all_rates.update(self.Reader.real_currencies_recalculated)
        all_rates.update(self.Reader.crypto_currencies_recalculated)
        assert all_rates == recalculate_to_floats

    def test_CurrencyReader_EUR_recalculation(self):
        self.Reader.base_currency = "EUR"
        recalculate_to_floats = {key: float(value) for key, value in self.Reader._raw_rates_data["rates"].items()}
        all_rates = {}
        all_rates.update(self.Reader.real_currencies_recalculated)
        all_rates.update(self.Reader.crypto_currencies_recalculated)
        assert all_rates != recalculate_to_floats
        assert self.Reader.real_currencies_recalculated.get("PLN") == 4.175038396575023
        assert self.Reader.real_currencies_recalculated.get("BTC") is None
        assert self.Reader.crypto_currencies_recalculated.get("BTC") is not None

    def test_CurrencyReader_recalculate_base(self):
        recalculate_to_floats = {key: float(value) for key, value in self.Reader._raw_rates_data["rates"].items()}
        all_rates = {}
        all_rates.update(self.Reader.real_currencies_recalculated)
        all_rates.update(self.Reader.crypto_currencies_recalculated)
        assert all_rates == recalculate_to_floats
        self.Reader.base_currency = "EUR"
        all_rates = {}
        all_rates.update(self.Reader.real_currencies_recalculated)
        all_rates.update(self.Reader.crypto_currencies_recalculated)
        assert all_rates != recalculate_to_floats
        assert self.Reader.real_currencies_recalculated.get("PLN") == 4.175038396575023

    @pytest.mark.parametrize(
        "height,expected",
        [(1.76, "NZD"), (1.86, "BGN"), (1.54, "AUD"), ["1.76", "NZD"], ["1,76", "NZD"], [" 1, 76 ", "NZD"]],
    )
    def test_CurrencyReader_height_matching(self, height, expected):
        finding = self.Reader.find_closest_currency(height)
        assert finding == expected

    @pytest.mark.parametrize(
        "height,expected",
        [[1.76, "TTD"], [1.86, "CNY"], [1.54, "BRL"], ["1.76", "TTD"], ["1,76", "TTD"], [" 1, 76 ", "TTD"]],
    )
    def test_CurrencyReader_height_matching_recalculation(self, height, expected):
        self.Reader.base_currency = "PLN"
        finding = self.Reader.find_closest_currency(height)
        assert finding == expected

    @pytest.mark.parametrize(
        "height,expected",
        [
            [1.76, "FARTCOIN"],
            [1.86, "WEMIX"],
            [1.54, "ARKM"],
            ["1.76", "FARTCOIN"],
            ["1,76", "FARTCOIN"],
            [" 1, 76 ", "FARTCOIN"],
        ],
    )
    def test_CurrencyReader_height_matching_crypto(self, height, expected):
        finding = self.Reader.find_closest_crypto(height)
        assert finding == expected

    @pytest.mark.parametrize(
        "height,expected",
        [[1.76, "BAKE"], [1.86, "PUPS"], [1.54, "DAO"], ["1.76", "BAKE"], ["1,76", "BAKE"], [" 1, 76 ", "BAKE"]],
    )
    def test_CurrencyReader_height_matching_crypto_recalculation(self, height, expected):
        self.Reader.base_currency = "PLN"
        finding = self.Reader.find_closest_crypto(height)
        assert finding == expected

    @pytest.mark.parametrize("function", ["find_closest_crypto", "find_closest_currency"])
    @pytest.mark.parametrize("height, exception", [(None, AssertionError), ("dupa", ValueError), ("", ValueError)])
    def test_height_incorrect_value(self, function, height, exception):
        with pytest.raises(exception):
            fun = getattr(self.Reader, function)
            fun(height)

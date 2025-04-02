import os
from pathlib import Path
from loguru import logger
import pytest
from dotenv import load_dotenv
from mock import Mock, patch
import json
from src.CurrencyReader import CurrencyReader

load_dotenv()
logger.configure(handlers={})


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
    Reader = CurrencyReader(os.getenv("STOCK_API"), base_currency)
    assert Reader is not None
    assert Reader.currencies_data_base is not None
    assert Reader.real_currencies_recalculated is not None
    assert Reader.crypto_currencied_recalculated is not None


def test_CurrencyReader_USD_recalculation(api_mock):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "USD")
    recalculate_to_floats = {
        key: float(value) for key, value in Reader.currencies_data_base["rates"].items()
    }
    all_rates = {}
    all_rates.update(Reader.real_currencies_recalculated)
    all_rates.update(Reader.crypto_currencied_recalculated)
    assert all_rates == recalculate_to_floats


def test_CurrencyReader_EUR_recalculation(api_mock):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "EUR")
    recalculate_to_floats = {
        key: float(value) for key, value in Reader.currencies_data_base["rates"].items()
    }
    all_rates = {}
    all_rates.update(Reader.real_currencies_recalculated)
    all_rates.update(Reader.crypto_currencied_recalculated)
    assert all_rates != recalculate_to_floats
    assert Reader.real_currencies_recalculated.get("PLN") == 4.175038396575023
    assert Reader.real_currencies_recalculated.get("BTC") is None
    assert Reader.crypto_currencied_recalculated.get("BTC") is not None


def test_CurrencyReader_recalculate_base(api_mock, new_base="EUR"):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "USD")
    recalculate_to_floats = {
        key: float(value) for key, value in Reader.currencies_data_base["rates"].items()
    }
    all_rates = {}
    all_rates.update(Reader.real_currencies_recalculated)
    all_rates.update(Reader.crypto_currencied_recalculated)
    assert all_rates == recalculate_to_floats
    Reader.recalculate_base(new_base)
    all_rates = {}
    all_rates.update(Reader.real_currencies_recalculated)
    all_rates.update(Reader.crypto_currencied_recalculated)
    assert all_rates != recalculate_to_floats
    assert Reader.real_currencies_recalculated.get("PLN") == 4.175038396575023


@pytest.mark.parametrize(
    "height,expected", [[1.76, "TTD"], [1.86, "CNY"], [1.54, "BRL"]]
)
def test_CurrencyReader_height_matching(api_mock, height, expected):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "PLN")
    finding = Reader.find_closest_currency(height)
    assert finding == expected


@pytest.mark.parametrize(
    "height,expected", [[1.76, "TTD"], [1.86, "CNY"], [1.54, "BRL"]]
)
def test_CurrencyReader_height_matching_recalculation(api_mock, height, expected):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "EUR")
    Reader.recalculate_base("PLN")
    finding = Reader.find_closest_currency(height)
    assert finding == expected


@pytest.mark.parametrize(
    "height,expected", [[1.76, "BAKE"], [1.86, "PUPS"], [1.54, "DAO"]]
)
def test_CurrencyReader_height_matching_crypto(api_mock, height, expected):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "PLN")
    finding = Reader.find_closest_crypto(height)
    assert finding == expected


@pytest.mark.parametrize(
    "height,expected", [[1.76, "BAKE"], [1.86, "PUPS"], [1.54, "DAO"]]
)
def test_CurrencyReader_height_matching_crypto_recalculation(
    api_mock, height, expected
):
    Reader = CurrencyReader(os.getenv("STOCK_API"), "EUR")
    Reader.recalculate_base("PLN")
    finding = Reader.find_closest_crypto(height)
    assert finding == expected

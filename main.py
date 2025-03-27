import sys

from dotenv import load_dotenv
import os
from loguru import logger
from src.CurrencyReader import CurrencyReader


def main():
    logger.info("Running main.py")
    load_dotenv()
    Reader = CurrencyReader(os.getenv("STOCK_API"), "PLN")
    x = Reader.find_closest_currency(1.76)
    print(x)
    sys.exit(0)


if __name__ == "__main__":
    main()

from dotenv import load_dotenv
import os
from loguru import logger
from src.CurrencyReader import CurrencyReader
import tkinter as tk

from src.Frontend import App
from utils import read_pyproject

CONFIG = read_pyproject()


def run_app():
    logger.info("Running main.py")
    load_dotenv()

    Reader = CurrencyReader(os.getenv("STOCK_API"), CONFIG["currency_reader"]["starting_currency"])

    root = tk.Tk()
    App(root, Reader)
    root.mainloop()


if __name__ == "__main__":
    run_app()


#
#
# print(response.choices[0].message.content)
#
# The BAKE symbol (🍞) represents

import threading
import time
import tkinter as tk
from src.CurrencyReader import CurrencyReader
from loguru import logger

from utils import read_pyproject

CONFIG = read_pyproject()


class App:
    def __init__(self, root: tk.Tk, logic: CurrencyReader):
        # Initial Configuration of window
        self.logic = logic
        self.root = root
        self.root.geometry("500x500")
        self.input_currency = ...
        self.input_height = ...
        self.currency_funfact = tk.StringVar(value="Funfact about currency")
        self.crypto_funfact = tk.StringVar(value="Funfact about crypto")
        self.current_currency_selected = tk.StringVar(
            value=f"Currently selected currency: {CONFIG['currency_reader']['starting_currency']}"
        )
        self.__draw_header_info()
        self.__draw_inputs()
        self.__draw_buttons()
        self.__draw_funfact_window()

    def __draw_header_info(self):
        textbox1 = tk.Message(self.root, textvariable=self.current_currency_selected, padx=5, width=300)
        textbox1.pack()

    def __draw_inputs(self):
        text1 = tk.Message(self.root, text="Type your country currency ISO symbol, ex. USD, PLN.", padx=5, width=300)
        text1.pack()
        self.input_currency = tk.Entry(self.root)
        self.input_currency.pack()
        text2 = tk.Message(self.root, text="Type your height", padx=5, width=300)
        text2.pack()
        self.input_height = tk.Entry(self.root)
        self.input_height.pack()

    def __draw_buttons(self):
        # Draw buttons
        btn1 = tk.Button(self.root, text="Download newest rates.", command=self.click_update)
        btn1.pack()

        btn2 = tk.Button(self.root, text="Change base currency.", command=self.change_base)
        btn2.pack(pady=5)

        btn3 = tk.Button(self.root, text="Find matching currency.", command=self.find_currency)
        btn3.pack(pady=5)

        btn4 = tk.Button(self.root, text="Find matching crypto.", command=self.find_crypto)
        btn4.pack(pady=5)

    def __draw_funfact_window(self):
        textbox1 = tk.Message(self.root, textvariable=self.currency_funfact, padx=5, width=300)
        textbox1.pack()
        textbox2 = tk.Message(self.root, textvariable=self.crypto_funfact, padx=5, pady=15, width=300)
        textbox2.pack()

    def click_update(self):
        print("Not implemented.")

    def change_base(self):
        new_base = self.input_currency.get()
        self.logic.base_currency = new_base
        self.current_currency_selected.set(f"Currently selected currency: {self.logic.base_currency}")

    def find_crypto(self):
        height = self.input_height.get()
        crypto_symbol = self.logic.find_closest_crypto(float(height))

        def __update_text():
            logger.info("FRONTEND: Updating text for crypto fact.")
            self.crypto_funfact.set("Looking for funfact for crypto.")
            self.logic.Deepseek.find_funfact(crypto_symbol, True)
            time.sleep(1)
            while self.logic.Deepseek.crypto_streaming:
                self.crypto_funfact.set(
                    f"Matched cryptocurrency symbol: {crypto_symbol}\n{self.logic.Deepseek.crypto_fact}"
                )
                time.sleep(0.5)
            logger.success("FRONTEND: Crypto fact updating finished")

        update_thread = threading.Thread(target=__update_text)
        update_thread.start()

    def find_currency(self):
        height = self.input_height.get()
        currency_symbol = self.logic.find_closest_currency(float(height))

        def __update_text():
            logger.info("FRONTEND: Updating text for currency fact")
            self.currency_funfact.set("Looking for funfact for currency.")
            self.logic.Deepseek.find_funfact(currency_symbol)
            time.sleep(1)
            while self.logic.Deepseek.currency_streaming:
                self.currency_funfact.set(
                    f"Matched currency symbol: {currency_symbol}\n{self.logic.Deepseek.currency_fact}"
                )
                time.sleep(0.5)
            logger.success("FRONTEND: Currency fact updating finished")

        update_thread = threading.Thread(target=__update_text)
        update_thread.start()

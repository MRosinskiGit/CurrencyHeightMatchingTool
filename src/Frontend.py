import threading
import time
import tkinter as tk
from src.CurrencyReader import CurrencyReader
from loguru import logger

from utils import read_pyproject

CONFIG = read_pyproject()


class App:
    """Main application class for the currency matching GUI.

    This class handles the graphical user interface and coordinates between
    user interactions and the business logic provided by CurrencyReader.

    Attributes:
        logic (CurrencyReader): The business logic handler for currency operations
        root (tk.Tk): The main application window
        input_currency (tk.Entry): Input field for currency symbols
        input_height (tk.Entry): Input field for user height
        currency_funfact (tk.StringVar): Variable holding currency fun fact text
        crypto_funfact (tk.StringVar): Variable holding cryptocurrency fun fact text
        current_currency_selected (tk.StringVar): Variable showing currently selected base currency
    """

    def __init__(self, root: tk.Tk, logic: CurrencyReader):
        """Initializes the application window and UI components.

        Args:
            root (tk.Tk): The root Tkinter window
            logic (CurrencyReader): The currency logic handler instance
        """
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
        """Draws the header information showing the current base currency."""
        textbox1 = tk.Message(self.root, textvariable=self.current_currency_selected, padx=5, width=300)
        textbox1.pack()

    def __draw_inputs(self):
        """Draws the input fields for currency symbol and user height."""
        text1 = tk.Message(self.root, text="Type your country currency ISO symbol, ex. USD, PLN.", padx=5, width=300)
        text1.pack()
        self.input_currency = tk.Entry(self.root)
        self.input_currency.pack()
        text2 = tk.Message(self.root, text="Type your height", padx=5, width=300)
        text2.pack()
        self.input_height = tk.Entry(self.root)
        self.input_height.pack()

    def __draw_buttons(self):
        """Draws all interactive buttons in the application."""
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
        """Draws the display area for currency and cryptocurrency fun facts."""
        textbox1 = tk.Message(self.root, textvariable=self.currency_funfact, padx=5, width=300)
        textbox1.pack()
        textbox2 = tk.Message(self.root, textvariable=self.crypto_funfact, padx=5, pady=15, width=300)
        textbox2.pack()

    def click_update(self):
        """Placeholder method for updating currency rates (currently not implemented)."""
        print("Not implemented.")

    def change_base(self):
        """Changes the base currency used for calculations.

        Reads the new currency symbol from input_currency field and updates
        the business logic and UI display.
        """
        new_base = self.input_currency.get()
        self.logic.base_currency = new_base
        self.current_currency_selected.set(f"Currently selected currency: {self.logic.base_currency}")

    def find_crypto(self):
        """Finds the cryptocurrency matching the user's height.

        Starts a background thread to:
        1. Get the closest cryptocurrency match
        2. Retrieve a fun fact about it
        3. Update the UI as the fact is being streamed
        """
        height = self.input_height.get()
        crypto_symbol = self.logic.find_closest_crypto(height)

        def __update_text():
            """Internal function to handle the crypto fact UI updates."""
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
        """Finds the currency matching the user's height.

        Starts a background thread to:
        1. Get the closest currency match
        2. Retrieve a fun fact about it
        3. Update the UI as the fact is being streamed
        """
        height = self.input_height.get()
        currency_symbol = self.logic.find_closest_currency(height)

        def __update_text():
            """Internal function to handle the currency fact UI updates."""
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

import threading

from openai import OpenAI
from loguru import logger
from utils import read_pyproject


CONFIG = read_pyproject()


class Facts:
    """A class to handle retrieval of fun facts about currencies and cryptocurrencies using AI.

    This class interfaces with an AI model to stream interesting facts about financial symbols.
    It supports concurrent streaming for both regular currencies and cryptocurrencies.

    Attributes:
        crypto_fact (str): The most recently retrieved cryptocurrency fact.
        crypto_streaming (bool): Flag indicating if cryptocurrency fact is currently being streamed.
        currency_fact (str): The most recently retrieved currency fact.
        currency_streaming (bool): Flag indicating if currency fact is currently being streamed.
    """

    def __init__(self, deepseek_api):
        """Initializes the Facts interface with the AI model.

        Args:
            deepseek_api (str): API key for accessing the AI model service.

        Note:
            Requires configuration from pyproject.toml for model settings.
        """
        logger.info("Initializing interface to AI")
        self.Model = OpenAI(api_key=deepseek_api, base_url=CONFIG["ai_model"]["api_url"])
        self.crypto_fact = ""
        self.crypto_streaming = False
        self.currency_fact = ""
        self.currency_streaming = False

    def find_funfact(self, currency_symbol, crypto=False):
        """Initiates streaming of a fun fact about the given currency symbol.

        Starts a background thread to retrieve the fact from the AI model without blocking.
        Handles both regular currencies and cryptocurrencies.

        Args:
            currency_symbol (str): The currency/cryptocurrency symbol to get facts about.
            crypto (bool, optional): Flag indicating if the symbol is a cryptocurrency.
                                    Defaults to False.

        Note:
            If streaming is already in progress for the requested type (crypto/currency),
            the request will be ignored with a warning.
        """
        logger.info(f"Starting downloading fact about {currency_symbol}. Crypto flag: {crypto}")

        def __download_stream():
            """Internal function to handle the streaming of facts from the AI model.

            Manages streaming flags and accumulates the response fragments into the
            appropriate fact attribute (crypto_fact or currency_fact).
            """
            if crypto:
                if self.crypto_streaming:
                    logger.warning("Crypto fact is already streamed.")
                    return
                self.crypto_fact = ""
                self.crypto_streaming = True
            else:
                if self.currency_streaming:
                    logger.warning("Currency fact is already streamed.")
                    return
                self.currency_fact = ""
                self.currency_streaming = True

            # TODO Download Deepseek Demo Tokeniser and check if Token usage can be reduced.
            response = self.Model.chat.completions.create(
                model=CONFIG["ai_model"]["model_v"],
                messages=[
                    {
                        "role": "system",
                        "content": "Random fun fact about currency symbol provided by user. Max 3 sentences",
                    },
                    {"role": "user", "content": currency_symbol},
                ],
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    fragment = chunk.choices[0].delta.content
                    if crypto:
                        self.crypto_fact += fragment
                    else:
                        self.currency_fact += fragment
            if crypto:
                self.crypto_streaming = False
            else:
                self.currency_streaming = False
            logger.success("Streaming completed.")
            logger.debug(f"""Data received: 
            \tCrypto fact: {self.crypto_fact}
            \rCrypto streaming flag: {self.crypto_streaming}
            \tCurrency fact: {self.currency_fact}
            \tCurrency streaming flag: {self.currency_streaming}""")

        update_funfact_thread = threading.Thread(target=__download_stream)
        update_funfact_thread.start()

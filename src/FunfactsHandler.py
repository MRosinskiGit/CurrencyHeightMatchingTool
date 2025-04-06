import threading

from openai import OpenAI
from loguru import logger
from utils import read_pyproject


CONFIG = read_pyproject()


class Facts:
    def __init__(self, deepseek_api):
        logger.info("Initializing interface to AI")
        self.Model = OpenAI(api_key=deepseek_api, base_url=CONFIG["ai_model"]["api_url"])
        self.crypto_fact = ""
        self.crypto_streaming = False
        self.currency_fact = ""
        self.currency_streaming = False

    def find_funfact(self, currency_symbol, crypto=False):
        logger.info(f"Starting downloading fact about {currency_symbol}. Crypto flag: {crypto}")

        def __download_stream():
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

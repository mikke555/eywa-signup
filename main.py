import random

import settings
from modules.api_client import Client
from modules.config import logger
from modules.utils import random_sleep, sleep


def main():
    try:
        with open("keys.txt") as file:
            keys = [row.strip() for row in file]

        if settings.SHUFFLE_KEYS:
            random.shuffle(keys)

        with open("proxies.txt") as file:
            proxies = [f"http://{row.strip()}" for row in file]

        if settings.USE_PROXY == False:
            logger.warning("Not using proxy \n")

        for index, private_key in enumerate(keys, start=1):
            total_keys = len(keys)
            client = Client(
                private_key=private_key,
                wallet_label=f"[{index}/{total_keys}]",
                proxy=random.choice(proxies) if settings.USE_PROXY else None,
            )

            wallet_exists = client.check_wallet()

            if not wallet_exists:
                client.auth()
                random_sleep(3, 5)
                client.check_wallet()

            if index < total_keys:
                sleep(*settings.SLEEP_BETWEEN_WALLETS)

    except Exception as error:
        logger.error(f"{client.label} Error processing wallet: {error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Cancelled by user")

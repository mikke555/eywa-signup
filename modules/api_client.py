import random

import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from fake_useragent import UserAgent

import settings
from modules.config import logger
from modules.utils import random_sleep, write_to_csv

base_url = "https://eywa-bot-api-service.eywa.fi"


class Client:
    def __init__(self, private_key, wallet_label, proxy=None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.label = f"{wallet_label} {self.address} |"
        self.ua = UserAgent()
        self.session = self.create_session(proxy)

        self.check_ip()

    def create_session(self, proxy):
        session = requests.Session()

        if proxy:
            session.proxies.update({"http": proxy, "https": proxy})

        session.headers.update(
            {
                "accept": "*/*",
                "user-agent": self.ua.random,
                "accept-language": "en-US,en;q=0.9",
                "accept": "https://app.crosscurve.fi",
                "referer": "https://app.crosscurve.fi/",
            }
        )

        return session

    def check_ip(self):
        proxy = self.session.proxies

        try:
            resp = self.session.get("https://httpbin.org/ip", proxies=proxy, timeout=10)
            ip = resp.json()["origin"]
            logger.info(f"{self.label} Current IP: {ip}")

        except Exception as error:
            logger.error(f"{self.label} Failed to get IP: {error}")

    def check_wallet(self):
        endpoint = f"/leaderboard/season2/{self.address}"

        resp = self.session.get(f"{base_url}{endpoint}")
        data = resp.json()

        if data["status"] == "error":
            logger.debug(f"{self.label} {data['message']}")
            return False

        data = data["data"]
        pts = sum(data["points"]["total"].values())

        write_to_csv(
            "wallets.csv",
            headers=["Wallet", "Rank", "Ref", "Points"],
            data=[self.address, data["rank"], data["refCode"], pts],
        )
        logger.debug(
            f"{self.label} Rank: {data['rank']}, Ref code {data['refCode']}, Total points: {pts}"
        )

        return True

    def get_message(self):
        endpoint = f"/auth/message/{self.address}"

        resp = self.session.get(f"{base_url}{endpoint}")
        data = resp.json()

        return data["data"]["message"]

    def sign_message(self, message):
        message_encoded = encode_defunct(text=message)
        signed_message = Account.sign_message(
            message_encoded, private_key=self.private_key
        )
        return "0x" + signed_message.signature.hex()

    def auth(self):
        endpoint = "/auth"

        message = self.get_message()
        random_sleep(3, 5)
        signature = self.sign_message(message)
        ref = random.choice(settings.REF_POOL).upper()

        payload = {
            "address": self.address,
            "ref": ref,
            "signature": signature,
        }

        resp = self.session.post(f"{base_url}/{endpoint}", json=payload)
        data = resp.json()

        if data.get("status") != "success":
            logger.warning(f"{self.label} {data['status']}: {data['message']}\n")
            return False

        logger.success(f"{self.label} Auth successful, used ref code {ref}")
        return True

from cryptography.fernet import Fernet
from bootstrap.config import config
import base64
import hmac
import hashlib


class Encryption:
    @staticmethod
    def __setKey(key: str):
        key_bytes = bytes.fromhex(key)
        return base64.urlsafe_b64encode(key_bytes)

    @staticmethod
    def encrypt(data: str, key: str = config("secret_key")) -> str:
        cipher = Fernet(Encryption.__setKey(key))
        return cipher.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(token: str, key: str = config("secret_key")) -> str:
        cipher = Fernet(Encryption.__setKey(key))
        return cipher.decrypt(token.encode()).decode()

    @staticmethod
    def encode(payload: str, signature: str) -> str:
        sig = hmac.new(
            config("secret_key").encode(), f"{signature}".encode(), hashlib.md5
        ).hexdigest()[:4]
        payload = f"{payload}|{sig}"
        return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")

    @staticmethod
    def decode(token: str, signature: str):
        payload = base64.urlsafe_b64decode(token + "==").decode()
        value, sig = payload.rsplit("|", 1)
        expected = hmac.new(
            config("secret_key").encode(), f"{signature}".encode(), hashlib.md5
        ).hexdigest()[:4]
        if sig != expected:
            raise ValueError("Invalid signature given.")
        return value

from passlib.context import CryptContext

password_ctx = CryptContext(schemes=["argon2"], deprecated="auto")


class Hash:
    @staticmethod
    def make(string: str) -> str:
        return password_ctx.hash(string)

    @staticmethod
    def verify(value: str, hashed: str) -> bool:
        return password_ctx.verify(value, hashed)

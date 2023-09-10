from cryptography.fernet import Fernet

from misc.data_convert import *

CRYPT_KEY = Fernet.generate_key()


class Crypt:

    def __init__(self) -> None:
        self.f = Fernet(CRYPT_KEY)

    def enc(self, data: str) -> str:
        token = self.f.encrypt(str_to_bytes(data))
        return bytes_to_str(token)

    def dec(self, data: str) -> str:
        string = self.f.decrypt(str_to_bytes(data))
        return bytes_to_str(string)

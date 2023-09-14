from cryptography.fernet import Fernet

from misc.data_convert import str_to_bytes, bytes_to_str

# Generate a cryptographic key for encryption and decryption
CRYPT_KEY = Fernet.generate_key()


class Crypt:
    """
    A class for performing data encryption and decryption using Fernet encryption.

    Attributes:
        None

    Methods:
        - __init__(self) -> None: Initializes the Crypt instance with a generated encryption key.
        - enc(self, data: str) -> str: Encrypts the input data and returns the encrypted token as a string.
        - dec(self, data: str) -> str: Decrypts the input data token and returns the decrypted string.

    """

    def __init__(self) -> None:
        """
        Initializes a Crypt instance with a generated encryption key.

        Args:
            None

        Returns:
            None
        """
        self.f = Fernet(CRYPT_KEY)

    def enc(self, data: str) -> str:
        """
        Encrypts the input data using Fernet encryption.

        Args:
            data (str): The data to be encrypted as a string.

        Returns:
            str: The encrypted data token as a string.
        """
        token = self.f.encrypt(str_to_bytes(data))
        return bytes_to_str(token)

    def dec(self, data: str) -> str:
        """
        Decrypts the input data token using Fernet decryption.

        Args:
            data (str): The encrypted data token as a string.

        Returns:
            str: The decrypted data as a string.
        """
        string = self.f.decrypt(str_to_bytes(data))
        return bytes_to_str(string)

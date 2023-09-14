def bytes_to_str(data: bytes) -> str:
    """
    Converts bytes data to a string.

    Args:
        data (bytes): The bytes data to be converted.

    Returns:
        str: The string representation of the bytes data.
    """
    return data.decode()


def str_to_bytes(string: str) -> bytes:
    """
    Converts a string to bytes.

    Args:
        string (str): The string to be converted to bytes.

    Returns:
        bytes: The bytes representation of the input string.
    """
    return string.encode()

def ERROR(message: str) -> None:
    """
    Throw an error, and exit cleanly.

    Args:
        message (str): The message to print out before exiting.
    """

    print(f"ERROR: {message}")
    exit(1)

import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    """Custom exception for the Network Security module."""

    def __init__(self, error_message, error_detail):
        self.error_message = error_message
        _, _, exc_tb = error_detail

        if exc_tb is not None:
            self.line_number = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
        else:
            self.line_number = None
            self.file_name = None

    def __str__(self):
        return f"Error occurred in script: [{self.file_name}] at line: [{self.line_number}] with message: [{self.error_message}]"

if __name__ == "__main__":
    try:
        logger.logging.info("This is a test log message.")
        a = 1 / 0  # Intentional ZeroDivisionError
        print(a)
    except Exception as e:
        exc_info = sys.exc_info()
        error = NetworkSecurityException(e, exc_info)
        logger.logging.error(error)
        raise error
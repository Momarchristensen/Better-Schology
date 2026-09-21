class AccountNotFound(Exception):
    """Raised when the account is not found"""

    pass


class InvalidCredentials(Exception):
    """Raised when the email or password is incorrect"""

    pass

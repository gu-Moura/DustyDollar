class InvalidOperationException(Exception):
    pass


class DatabaseWritingException(Exception):
    pass


class DepositOperationException(Exception):
    pass


class AccountCreationException(Exception):
    pass


class TransactionCreationException(Exception):
    pass


class WithdrawalOperationException(Exception):
    pass


class AccountStatusChangeException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


class PersonCreationException(Exception):
    pass

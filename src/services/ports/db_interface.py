from abc import ABC, abstractmethod
from typing import Union, List, Optional

from src.models.entities import Account, Person, Transaction


class DBInterface(ABC):
    @abstractmethod
    def create_new_account(self, new_account: Account, password: str):
        raise NotImplementedError

    @abstractmethod
    def create_new_person(self, new_person: Person):
        raise NotImplementedError

    @abstractmethod
    def deposit_into_account(self, account_id: int, amount: float):
        raise NotImplementedError

    @abstractmethod
    def get_balance(self, account_id: int) -> Union[float, None]:
        raise NotImplementedError

    @abstractmethod
    def withdraw_from_account(self, account_id: int, amount: float):
        raise NotImplementedError

    @abstractmethod
    def change_account_active_status(self, account_id: int, active: bool):
        raise NotImplementedError

    @abstractmethod
    def get_extract_from_account(self, account_id: int, days: int = 30) -> List[Transaction]:
        raise NotImplementedError

    @abstractmethod
    def make_transaction(self, account_id: int, amount: float) -> Transaction:
        raise NotImplementedError

    @abstractmethod
    def check_account_active(self, account_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def reached_withdrawal_limit(self, account_id: int, withdrawal_amount: float) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_account_with_password(self, account_id: int, password: str) -> Optional[Account]:
        raise NotImplementedError
from datetime import datetime
from typing import Union, List, Optional, Tuple

from src.models.entities import Account, Person, Transaction, AccountType
from src.services.ports.db_interface import DBInterface


class MockDBInterface(DBInterface):
    def create_new_account(self, new_account: Account, password: str):
        return None

    def create_new_person(self, new_person: Person):
        return None

    def deposit_into_account(self, account_id: int, amount: float):
        return None

    def get_balance(self, account_id: int) -> Union[float, None]:
        return 100.0

    def withdraw_from_account(self, account_id: int, amount: float):
        return None

    def change_account_active_status(self, account_id: int, active: bool):
        return None

    def get_extract_from_account(self, account_id: int, days: int = 30) -> List[Transaction]:
        rows = [
            (1, account_id, 103.52, datetime.strptime('2023-12-12', '%Y-%m-%d')),
            (2, account_id, 128.98, datetime.strptime('2023-12-15', '%Y-%m-%d'))
        ]
        return [Transaction.from_dict(dict(
            id_transacao=row[0],
            id_conta=row[1],
            valor=row[2],
            data_transacao=row[3].strftime('%Y-%m-%d')
        )) for row in rows]

    def _make_transaction(self, account_id: int, amount: float) -> Transaction:
        transaction = {
            "id_conta": account_id,
            "valor": amount,
            "data_transacao": datetime.now().strftime("%Y-%m-%d"),
            "id_transacao": 1
        }
        return Transaction.from_dict(transaction)

    def check_account_active(self, account_id: int) -> bool:
        if account_id < 0:
            return False
        return True

    def reached_withdrawal_limit(self, account_id: int, withdrawal_amount: float) -> bool:
        return False

    def get_account(self, account_id: int) -> tuple[Account, str]:
        return Account.from_dict({
            "id_conta": account_id,
            "id_pessoa": 1,
            "saldo": 100.0,
            "limite_saque_diario": 1000.0,
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": datetime.now().date().strftime('%Y-%m-%d'),
        }), 'password'

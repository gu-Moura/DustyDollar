from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from src.exceptions import InvalidOperationException


class AccountType(Enum):
    Checking = 1
    Savings = 2


class OperationType(Enum):
    Deposit = 1
    Withdrawal = 2


@dataclass
class Person:
    id_pessoa: Optional[int]
    nome: str
    cpf: str
    data_nascimento: datetime.date

    @staticmethod
    def from_dict(data: dict):
        return Person(
            id_pessoa=int(data.get('id_pessoa')) if data.get('id_pessoa') else None,
            nome=data.get('nome'),
            cpf=data.get('cpf'),
            data_nascimento=datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').date()
        )

    def to_dict(self) -> dict:
        return dict(
            id_pessoa=self.id_pessoa,
            nome=self.nome,
            cpf=self.cpf,
            data_nascimento=self.data_nascimento
        )


@dataclass
class Transaction:
    id_transacao: Optional[int]
    id_conta: int
    valor: float
    data_transacao: datetime.date

    @staticmethod
    def from_dict(data: dict):
        return Transaction(
            id_transacao=int(data.get('id_transacao')) if data.get('id_transacao') else None,
            id_conta=int(data.get('id_conta')),
            valor=float(data.get('valor')),
            data_transacao=datetime.strptime(data.get("data_transacao"), '%Y-%m-%d').date()
        )

    def to_dict(self) -> dict:
        return dict(
            id_transacao=self.id_transacao,
            id_conta=self.id_conta,
            valor=self.valor,
            data_transacao=self.data_transacao.strftime('%Y-%m-%d')
        )


@dataclass
class Account:
    id_conta: Optional[int]
    id_pessoa: int
    saldo: float
    limite_saque_diario: float
    flag_ativo: bool
    tipo_conta: AccountType
    data_criacao: datetime.date

    @staticmethod
    def from_dict(data: dict):
        return Account(
            id_conta=int(data.get('id_conta')) if data.get('id_conta') else None,
            id_pessoa=int(data.get('id_pessoa')),
            saldo=float(data.get('saldo')),
            limite_saque_diario=float(data.get('limite_saque_diario')),
            flag_ativo=bool(data.get('flag_ativo')),
            tipo_conta=AccountType(int(data.get('tipo_conta'))),
            data_criacao=datetime.strptime(data.get("data_criacao"), '%Y-%m-%d').date()
        )

    def to_dict(self) -> dict:
        return dict(
            id_conta=self.id_conta,
            id_pessoa=self.id_pessoa,
            saldo=self.saldo,
            limite_saque_diario=self.limite_saque_diario,
            flag_ativo=self.flag_ativo,
            tipo_conta=self.tipo_conta.value,
            data_criacao=self.data_criacao
        )


@dataclass
class OperationDTO:
    account_id: int
    amount: float
    operation_type: OperationType

    @staticmethod
    def from_dict(data: dict):
        if data.get('operation_type') not in ['Deposit', 'Withdrawal']:
            raise InvalidOperationException('You can only use valid operations such as Deposit or Withdrawal.')
        return OperationDTO(
            account_id=int(data.get('account_id')),
            amount=abs(float(data.get('amount'))),
            operation_type=OperationType(1) if data.get('operation_type') == 'Deposit' else OperationType(2)
        )

    def to_dict(self) -> dict:
        return dict(
            account_id=self.account_id,
            amount=self.amount,
            operation_type=self.operation_type.name
        )


@dataclass
class AccountStatusDTO:
    account_id: int
    account_active: bool

    @staticmethod
    def from_dict(data: dict):
        return AccountStatusDTO(
            account_id=int(data.get('account_id')),
            account_active=bool(data.get('account_active'))
        )

    def to_dict(self):
        return dict(
            account_id=self.account_id,
            account_active=self.account_active
        )


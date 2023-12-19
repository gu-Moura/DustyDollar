from dataclasses import dataclass
from datetime import datetime


@dataclass
class Pessoa:
    id_pessoa: int
    nome: str
    cpf: str
    data_nascimento: datetime.date

    @staticmethod
    def from_dict(data: dict):
        return Pessoa(
            id_pessoa=int(data.get('id_pessoa')),
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
class Transacao:
    id_transacao: int
    id_conta: int
    valor: float
    data_transacao: datetime.date

    @staticmethod
    def from_dict(data: dict):
        return Transacao(
            id_transacao=int(data.get('id_transacao')),
            id_conta=int(data.get('id_conta')),
            valor=float(data.get('valor')),
            data_transacao=datetime.strptime(data.get("data_transacao"), '%Y-%m-%d').date()
        )

    def to_dict(self) -> dict:
        return dict(
            id_transacao=self.id_transacao,
            id_conta=self.id_conta,
            valor=self.valor,
            data_transacao=self.data_transacao
        )


@dataclass
class Conta:
    id_conta: int
    id_pessoa: int
    saldo: float
    limite_saque_diario: float
    flag_ativo: bool
    tipo_conta: int
    data_criacao: datetime.date

    @staticmethod
    def from_dict(data: dict):
        return Conta(
            id_conta=int(data.get('id_conta')),
            id_pessoa=int(data.get('id_pessoa')),
            saldo=float(data.get('saldo')),
            limite_saque_diario=float(data.get('limite_saque_diario')),
            flag_ativo=bool(data.get('flag_ativo')),
            tipo_conta=int(data.get('tipo_conta')),
            data_criacao=datetime.strptime(data.get("data_criacao"), '%Y-%m-%d').date()
        )

    def to_dict(self) -> dict:
        return dict(
            id_conta=self.id_conta,
            id_pessoa=self.id_pessoa,
            saldo=self.saldo,
            limite_saque_diario=self.limite_saque_diario,
            flag_ativo=self.flag_ativo,
            tipo_conta=self.tipo_conta,
            data_criacao=self.data_criacao
        )
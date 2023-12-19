from datetime import datetime, timedelta
from typing import Union, List, Optional

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DECIMAL, Table, MetaData, Text, insert, \
    func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import db_url, bcrypt
from models.entities import Account, Transaction, Person

from exceptions import InvalidPasswordException
from services.ports.db_interface import DBInterface

engine = create_engine(db_url)
metadata = MetaData()
Base = declarative_base()
Session = sessionmaker(bind=engine)

conta_table = Table('conta', metadata,
                    Column('id_conta', Integer, primary_key=True, autoincrement=True),
                    Column('id_pessoa', Integer, nullable=True),
                    Column('saldo', DECIMAL(precision=10, scale=0), nullable=True),
                    Column('limite_saque_diario', DECIMAL(precision=10, scale=0), nullable=True),
                    Column('flag_ativo', Boolean, nullable=True),
                    Column('tipo_conta', DECIMAL(precision=10, scale=0), nullable=True),
                    Column('data_criacao', Date, nullable=True),
                    Column('senha', Text, nullable=False),
                    )

pessoa_table = Table('pessoa', metadata,
                     Column('id_pessoa', Integer, primary_key=True, autoincrement=True),
                     Column('nome', Text, nullable=True),
                     Column('cpf', String(11), nullable=True),
                     Column('data_nascimento', Date, nullable=True),
                     )

transactions_table = Table('transacao', metadata,
                           Column('id_transacao', Integer, primary_key=True, autoincrement=True),
                           Column('id_conta', Integer, nullable=True),
                           Column('valor', DECIMAL(precision=10, scale=0), nullable=True),
                           Column('data_transacao', Date, nullable=True),
                           )

metadata.create_all(engine)


class SQLAlchemyDBService(DBInterface):
    def create_new_account(self, new_account: Account, password: str):
        new_row = new_account.to_dict()
        new_row['senha'] = bcrypt.generate_password_hash(password).decode('utf-8')
        for key, item in new_row.copy().items():
            if item is None:
                new_row.pop(key)

        session = Session()
        session.connection().execute(insert(conta_table), new_row)
        session.commit()
        session.close()

    def create_new_person(self, new_person: Person):
        new_row = new_person.to_dict()
        for key, item in new_row.copy().items():
            if not item:
                new_row.pop(key)

        session = Session()
        session.connection().execute(insert(pessoa_table), new_row)
        session.commit()
        session.close()

    def deposit_into_account(self, account_id: int, amount: float):
        session = Session()

        session.connection().execute(
            conta_table.update()
            .where(conta_table.c.id_conta == account_id)
            .values(saldo=conta_table.c.saldo + abs(amount))
        )

        session.commit()
        session.close()

    def get_balance(self, account_id: int) -> Union[float, None]:
        session = Session()
        result = session.query(conta_table).filter_by(id_conta=account_id).first()
        current_balance = result.saldo if result is not None else None
        session.close()
        return current_balance

    def withdraw_from_account(self, account_id: int, amount: float):
        session = Session()
        session.connection().execute(
            conta_table.update()
            .where(conta_table.c.id_conta == account_id)
            .values(saldo=conta_table.c.saldo - abs(amount))
        )
        session.commit()
        session.close()

    def change_account_active_status(self, account_id: int, active: bool):
        session = Session()
        session.connection().execute(
            conta_table.update()
            .where(conta_table.c.id_conta == account_id)
            .values(flag_ativo=active)
        )
        session.commit()
        session.close()

    def get_extract_from_account(self, account_id: int, days: int = 30) -> List[Transaction]:
        since_day = datetime.now() - timedelta(days=days)
        session = Session()
        result = session.query(transactions_table).filter(transactions_table.c.id_conta == account_id,
                                                          transactions_table.c.data_transacao >= since_day).all()
        session.close()
        extract = [Transaction.from_dict(dict(
            id_transacao=row[0],
            id_conta=row[1],
            valor=row[2],
            data_transacao=row[3].strftime('%Y-%m-%d')
        )) for row in result]
        return extract

    def make_transaction(self, account_id: int, amount: float) -> Transaction:
        session = Session()
        transaction = {
            "id_conta": account_id,
            "valor": amount,
            "data_transacao": datetime.now().strftime("%Y-%m-%d")
        }
        result = session.execute(insert(transactions_table), transaction)
        session.commit()
        session.close()

        transaction['id_transacao'] = result.inserted_primary_key[0]
        return Transaction.from_dict(transaction)

    def check_account_active(self, account_id: int) -> bool:
        session = Session()
        result = session.query(conta_table).filter_by(id_conta=account_id).first()
        session.close()

        return bool(result.flag_ativo)

    def reached_withdrawal_limit(self, account_id: int, withdrawal_amount: float) -> bool:
        session = Session()
        withdrawal_limit = (session.query(conta_table.c.limite_saque_diario)
                            .filter_by(id_conta=account_id)
                            .scalar())
        total_withdrawn = (session.query(func.sum(func.abs(transactions_table.c.valor)))
                           .filter(transactions_table.c.id_conta == account_id,
                                   transactions_table.c.valor < 0.0,
                                   transactions_table.c.data_transacao == datetime.now().date().strftime('%Y-%m-%d'))
                           .scalar()
                           ) or 0.0
        session.close()
        return True if (total_withdrawn > withdrawal_limit or
                        withdrawal_amount > withdrawal_limit) else False

    def get_account_with_password(self, account_id: int, password: str) -> Optional[Account]:
        session = Session()
        result = session.query(conta_table).filter_by(id_conta=account_id).first()
        session.close()
        if not bcrypt.check_password_hash(result.senha, password):
            raise InvalidPasswordException

        return Account.from_dict(dict(
            id_conta=result[0],
            id_pessoa=result[1],
            saldo=result[2],
            limite_saque_diario=result[3],
            flag_ativo=result[4],
            tipo_conta=result[5],
            data_criacao=result[6].strftime('%Y-%m-%d')
        )) if result is not None else None

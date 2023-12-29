from datetime import datetime, timedelta, date
from typing import Union, List, Optional, Tuple

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, DECIMAL, Table, MetaData, Text, insert, \
    func, Engine
from sqlalchemy.orm import sessionmaker, Session

from src.exceptions import DepositOperationException, TransactionCreationException, WithdrawalOperationException, \
    AccountCreationException, PersonCreationException, AccountStatusChangeException, GetBalanceException, \
    GetStatementException, AccountStatusCheckException, WithdrawalLimitCheckException, AccountRetrievalException, \
    AccountRetrievalException
from src.models.entities import Account, Transaction, Person
from src.services.ports.db_interface import DBInterface


class SQLAlchemyDBService(DBInterface):
    def __init__(self, db_url: str):
        self.metadata = MetaData()
        self.engine, self.Session = self._create_engine(db_url)
        self.conta_table = Table('conta', self.metadata,
                                 Column('id_conta', Integer, primary_key=True, autoincrement=True),
                                 Column('id_pessoa', Integer, nullable=True),
                                 Column('saldo', DECIMAL(precision=10, scale=0), nullable=True),
                                 Column('limite_saque_diario', DECIMAL(precision=10, scale=0), nullable=True),
                                 Column('flag_ativo', Boolean, nullable=True),
                                 Column('tipo_conta', DECIMAL(precision=10, scale=0), nullable=True),
                                 Column('data_criacao', Date, nullable=True),
                                 Column('senha', Text, nullable=False),
                                 )

        self.pessoa_table = Table('pessoa', self.metadata,
                                  Column('id_pessoa', Integer, primary_key=True, autoincrement=True),
                                  Column('nome', Text, nullable=True),
                                  Column('cpf', String(11), nullable=True),
                                  Column('data_nascimento', Date, nullable=True),
                                  )

        self.transactions_table = Table('transacao', self.metadata,
                                        Column('id_transacao', Integer, primary_key=True, autoincrement=True),
                                        Column('id_conta', Integer, nullable=True),
                                        Column('valor', DECIMAL(precision=10, scale=0), nullable=True),
                                        Column('data_transacao', Date, nullable=True),
                                        )

    def _create_engine(self, db_url: str) -> tuple[None, None] | tuple[Engine, sessionmaker[Session]]:
        if not db_url:
            return None, None
        engine = create_engine(db_url)
        _sessionmaker = sessionmaker(bind=engine)

        self.metadata.create_all(engine)

        return engine, _sessionmaker

    def create_new_account(self, new_account: Account, password: str) -> Account:
        new_row = {key: item for key, item in new_account.to_dict().items() if item is not None}
        new_row.update(senha=password)

        session = self.Session()
        try:
            insert_row = insert(self.conta_table)
            session.execute(insert_row, new_row)
            session.commit()

            new_account_id = session.query(self.conta_table.c.id_conta).filter_by(senha=password).scalar()
            new_row['id_conta'] = new_account_id
            return Account.from_dict(new_row)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise AccountCreationException(e)
        finally:
            session.close()

    def create_new_person(self, new_person: Person) -> Person:
        new_row = {key: item for key, item in new_person.to_dict().items() if item is not None}

        session = self.Session()
        try:
            insert_row = insert(self.pessoa_table)
            session.execute(insert_row, new_row)
            session.commit()

            new_person_id = session.query(self.pessoa_table.c.id_pessoa).filter_by(cpf=new_person.cpf).scalar()
            new_row['id_pessoa'] = new_person_id
            return Person.from_dict(new_row)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise PersonCreationException(e)
        finally:
            session.close()

    def deposit_into_account(self, account_id: int, amount: float) -> Transaction:
        session = self.Session()
        try:
            session.execute(
                self.conta_table.update()
                .where(self.conta_table.c.id_conta == account_id)
                .values(saldo=self.conta_table.c.saldo + abs(amount))
            )
            session.commit()
            return self._make_transaction(account_id, abs(amount), datetime.now().date())
        except TransactionCreationException as e:
            session.execute(
                self.conta_table.update()
                .where(self.conta_table.c.id_conta == account_id)
                .values(saldo=self.conta_table.c.saldo - abs(amount))
            )
            session.commit()
            raise DepositOperationException(e)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise DepositOperationException(e)
        finally:
            session.close()

    def withdraw_from_account(self, account_id: int, amount: float) -> Transaction:
        session = self.Session()
        try:
            session.execute(
                self.conta_table.update()
                .where(self.conta_table.c.id_conta == account_id)
                .values(saldo=self.conta_table.c.saldo - abs(amount))
            )

            return self._make_transaction(account_id, -abs(amount), datetime.now().date())
        except TransactionCreationException as e:
            session.execute(
                self.conta_table.update()
                .where(self.conta_table.c.id_conta == account_id)
                .values(saldo=self.conta_table.c.saldo + abs(amount))
            )
            session.commit()
            raise DepositOperationException(e)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise DepositOperationException(e)
        finally:
            session.commit()
            session.close()

    def get_balance(self, account_id: int) -> Union[float, None]:
        session = self.Session()
        try:
            saldo = (session.query(self.conta_table.c.saldo)
                     .filter_by(id_conta=account_id).scalar())
            return saldo if saldo is not None else None
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise GetBalanceException(e)
        finally:
            session.close()

    def set_account_active_status(self, account_id: int, active: bool) -> bool:
        session = self.Session()
        try:
            session.execute(
                self.conta_table.update()
                .where(self.conta_table.c.id_conta == account_id)
                .values(flag_ativo=active)
            )
            session.commit()
            return self.check_account_active(account_id)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise AccountStatusChangeException(e)
        finally:
            session.close()

    def get_statement_from_account(self, account_id: int, days: int = 30) -> List[Transaction]:
        since_day = datetime.now() - timedelta(days=days)
        session = self.Session()
        try:
            result = (session.query(self.transactions_table)
                      .filter(self.transactions_table.c.id_conta == account_id,
                              self.transactions_table.c.data_transacao >= since_day).all())
            extract = [Transaction.from_dict(dict(
                id_transacao=row[0],
                id_conta=row[1],
                valor=row[2],
                data_transacao=row[3].strftime('%Y-%m-%d')
            )) for row in result]
            return extract
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise GetStatementException(e)
        finally:
            session.close()

    def _make_transaction(self, account_id: int, amount: float, transaction_date: date) -> Transaction:
        new_transaction = {
            "id_conta": account_id,
            "valor": amount,
            "data_transacao": transaction_date.strftime("%Y-%m-%d")
        }
        session = self.Session()
        try:
            insert_row = insert(self.transactions_table)
            result = session.execute(insert_row, new_transaction)
            session.commit()
        except Exception as e:
            raise TransactionCreationException(e)
        finally:
            session.close()

        completed_transaction = {
            **new_transaction,
            'id_transacao': result.inserted_primary_key[0]
        }
        return Transaction.from_dict(completed_transaction)

    def check_account_active(self, account_id: int) -> bool:
        session = self.Session()
        try:
            account_active = session.query(self.conta_table.c.flag_ativo).filter_by(id_conta=account_id).scalar()
            return bool(account_active)
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise AccountStatusCheckException(e)
        finally:
            session.close()

    def reached_withdrawal_limit(self, account_id: int, withdrawal_amount: float) -> bool:
        session = self.Session()
        try:
            withdrawal_limit = (session.query(self.conta_table.c.limite_saque_diario)
                                .filter_by(id_conta=account_id)
                                .scalar())
            total_withdrawn = (session.query(func.sum(func.abs(self.transactions_table.c.valor)))
                               .filter(self.transactions_table.c.id_conta == account_id,
                                       self.transactions_table.c.valor < 0.0,
                                       self.transactions_table.c.data_transacao == datetime.now().date().strftime(
                                           '%Y-%m-%d'))
                               .scalar()
                               )
            return True if (total_withdrawn + withdrawal_amount) > withdrawal_limit else False
        except (sqlalchemy.exc.SQLAlchemyError, TypeError) as e:
            raise WithdrawalLimitCheckException(e)
        finally:
            session.close()

    def get_account(self, account_id: int) -> Tuple[Account, str]:
        session = self.Session()
        try:
            result = session.query(self.conta_table).filter_by(id_conta=account_id).first()
            if result is None:
                raise AccountRetrievalException("Account not found!")

            return Account.from_dict(dict(
                id_conta=result[0],
                id_pessoa=result[1],
                saldo=result[2],
                limite_saque_diario=result[3],
                flag_ativo=result[4],
                tipo_conta=result[5],
                data_criacao=result[6].strftime('%Y-%m-%d')
            )), result[7]  # result[7] is the store password hash
        except (sqlalchemy.exc.SQLAlchemyError, TypeError) as e:
            raise AccountRetrievalException(e)
        finally:
            session.close()

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, call

import src.services.db_service

from src.models import entities
from src.models.entities import Account, Transaction
from src.services.db_service import SQLAlchemyDBService


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.session_mock = Mock()
        self.mock_sqla = SQLAlchemyDBService("")
        self.mock_sqla.engine = Mock()
        self.mock_sqla.Session = Mock(return_value=self.session_mock)
        self.mock_sqla.conta_table = Mock()
        self.mock_sqla.transactions_table = Mock()
        self.mock_sqla.pessoa_table = Mock()

    def tearDown(self):
        self.session_mock = None
        self.mock_sqla.engine = None
        self.mock_sqla.Session = None
        self.mock_sqla.conta_table = None
        self.mock_sqla.transactions_table = None
        self.mock_sqla.pessoa_table = None
        self.mock_sqla = None

    @patch('src.services.db_service.insert')
    def test_create_new_account(self, mock_insert: Mock):
        account_dict = {
            "id_conta": 1,
            "id_pessoa": 1,
            "saldo": 100.0,
            "limite_saque_diario": 1000,
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": "2022-06-18",
        }
        account = entities.Account.from_dict(account_dict)

        self.mock_sqla.create_new_account(account, '123456')

        # Asserts
        mock_insert.assert_called_once_with(self.mock_sqla.conta_table)
        self.mock_sqla.Session.assert_called_once()
        self.session_mock.execute.assert_called_once_with(mock_insert.return_value,
                                                          {**account.to_dict(), "senha": '123456'})
        self.session_mock.commit.assert_called_once()
        self.session_mock.close.assert_called_once()

    @patch('src.services.db_service.insert')
    def test_create_new_person(self, mock_insert: Mock):
        person_dict = {
            "id_pessoa": 1,
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": "1999-01-01"
        }
        person = entities.Person.from_dict(person_dict)

        self.mock_sqla.create_new_person(person)

        # Asserts
        mock_insert.assert_called_once_with(self.mock_sqla.pessoa_table)
        self.mock_sqla.Session.assert_called_once()
        self.session_mock.execute.assert_called_once_with(mock_insert.return_value, person.to_dict())
        self.session_mock.commit.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_deposit_into_account(self):
        account_id = 1
        amount = 1.0

        self.mock_sqla.conta_table.c.saldo = amount
        self.mock_sqla.conta_table.c.id_conta = account_id
        self.mock_sqla.deposit_into_account(account_id, amount)

        # Asserts
        self.mock_sqla.Session.assert_called()
        self.mock_sqla.conta_table.update.assert_called_once()
        (self.mock_sqla.conta_table.update.return_value.where
         .assert_called_once_with(self.mock_sqla.conta_table.c.id_conta == account_id))
        (self.mock_sqla.conta_table.update.return_value.where.return_value.values
         .assert_called_once_with(saldo=self.mock_sqla.conta_table.c.saldo + abs(amount)))
        self.session_mock.execute.assert_called_once()
        self.session_mock.commit.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_get_balance(self):
        account_id = 1
        current_balance = 12344.23

        self.session_mock.query.return_value.filter_by.return_value.scalar.return_value = current_balance
        check_balance = self.mock_sqla.get_balance(account_id)

        # Asserts
        self.assertEqual(check_balance, current_balance)
        self.mock_sqla.Session.assert_called()
        self.session_mock.query.assert_called_once_with(self.mock_sqla.conta_table.c.saldo)
        self.session_mock.query.return_value.filter_by.assert_called_once_with(id_conta=account_id)
        self.session_mock.query.return_value.filter_by.return_value.scalar.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_get_balance_account_not_found(self):
        account_id = 1

        self.session_mock.query.return_value.filter_by.return_value.scalar.return_value = None
        self.mock_sqla.get_balance(account_id)

        # Asserts
        self.mock_sqla.Session.assert_called()
        self.session_mock.query.assert_called_once_with(self.mock_sqla.conta_table.c.saldo)
        self.session_mock.query.return_value.filter_by.assert_called_once_with(id_conta=account_id)
        self.session_mock.query.return_value.filter_by.return_value.scalar.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_withdraw_from_account(self):
        account_id = 1
        amount = 1.0

        self.mock_sqla.conta_table.c.saldo = 0
        self.mock_sqla.withdraw_from_account(account_id, amount)

        # Asserts
        self.mock_sqla.Session.assert_called()
        (self.mock_sqla.conta_table.update.return_value.where
         .assert_called_once_with(self.mock_sqla.conta_table.c.id_conta == account_id))
        (self.mock_sqla.conta_table.update.return_value.where.return_value.values
         .assert_called_once_with(saldo=self.mock_sqla.conta_table.c.saldo - abs(amount)))
        self.mock_sqla.conta_table.update.assert_called_once()
        self.session_mock.execute.assert_called_once()
        self.session_mock.commit.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_change_account_active_status(self):
        account_id = 1
        active = False

        self.mock_sqla.conta_table.c.id_conta = account_id

        self.mock_sqla.set_account_active_status(account_id, active)

        # Asserts
        self.mock_sqla.conta_table.update.return_value.where.assert_called_once_with(True)
        self.mock_sqla.conta_table.update.return_value.where.return_value.values.assert_called_once_with(
            flag_ativo=active)
        self.mock_sqla.Session.assert_called()
        self.mock_sqla.conta_table.update.assert_called_once()
        self.session_mock.execute.assert_called_once()
        self.session_mock.commit.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_get_statement_from_account(self):
        expected_account_id = 12321
        days_prior = 30
        expected_since_day = datetime.now() - timedelta(days=days_prior)
        expected_rows = [
            (1, expected_account_id, 103.52, datetime.strptime('2023-12-12', '%Y-%m-%d')),
            (2, expected_account_id, 128.98, datetime.strptime('2023-12-15', '%Y-%m-%d'))
        ]

        expected_transactions = [
            Transaction(1, 12321, 103.52, datetime.strptime('2023-12-12', '%Y-%m-%d').date()),
            Transaction(2, 12321, 128.98, datetime.strptime('2023-12-15', '%Y-%m-%d').date())
        ]

        self.session_mock.query.return_value.filter.return_value.all.return_value = expected_rows
        self.mock_sqla.transactions_table.c.data_transacao = datetime(year=2023, month=12, day=12)

        statement = self.mock_sqla.get_statement_from_account(account_id=12321, days=30)

        # Asserts
        self.mock_sqla.Session.assert_called()
        self.session_mock.query.assert_called_once_with(self.mock_sqla.transactions_table)
        self.session_mock.query.return_value.filter.assert_called_once_with(
            self.mock_sqla.transactions_table.c.id_conta == expected_account_id,
            self.mock_sqla.transactions_table.c.data_transacao >= expected_since_day
        )
        self.session_mock.close.assert_called_once()
        self.assertEqual(statement, expected_transactions)

    @patch('src.services.db_service.insert')
    def test_make_transaction(self, mock_insert: Mock):
        account_id = 1
        amount = 1.0
        transaction_date = datetime.now().strftime("%Y-%m-%d")
        expected_transaction_id = 1
        expected_transaction_dict = {
            "id_conta": account_id,
            "valor": amount,
            "data_transacao": transaction_date
        }
        expected_transaction = Transaction.from_dict(
            {**expected_transaction_dict, "id_transacao": expected_transaction_id})
        self.session_mock.execute.return_value = Mock()
        self.session_mock.execute.return_value.inserted_primary_key = [expected_transaction_id]

        transaction = self.mock_sqla.make_transaction(account_id=account_id, amount=amount)

        self.assertEqual(expected_transaction, transaction)
        mock_insert.assert_called_once_with(self.mock_sqla.transactions_table)
        self.mock_sqla.Session.assert_called()
        self.session_mock.execute.assert_called_once_with(mock_insert.return_value, expected_transaction_dict)
        self.session_mock.commit.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_check_account_active(self):
        account_id = 1
        expected_account_status = True
        self.session_mock.query.return_value.filter_by.return_value.scalar.return_value = expected_account_status

        account_status = self.mock_sqla.check_account_active(account_id=account_id)

        self.assertEqual(expected_account_status, account_status)
        self.mock_sqla.Session.assert_called()
        self.session_mock.query.assert_called_once_with(self.mock_sqla.conta_table.c.flag_ativo)
        self.session_mock.query.return_value.filter_by.assert_called_once_with(id_conta=account_id)
        self.session_mock.query.return_value.filter_by.return_value.scalar.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_check_account_active_invalid_account(self):
        account_id = 1
        expected_account_status = None
        self.session_mock.query.return_value.filter_by.return_value.scalar.return_value = expected_account_status

        account_status = self.mock_sqla.check_account_active(account_id=account_id)

        self.assertEqual(expected_account_status, account_status)

    @patch("src.services.db_service.func")
    def test_reached_withdrawal_limit(self, mock_func: Mock):
        account_id = 1
        withdrawal_limit = 1023.00
        withdrawal_amount = 1000.00
        transaction_date = datetime.now().date().strftime('%Y-%m-%d')
        last_withdrawal = -123.65

        mock_func.sum = Mock()
        mock_func.abs = Mock()

        self.session_mock.query.return_value.filter_by.return_value.scalar.return_value = withdrawal_limit

        self.mock_sqla.transactions_table.c.id_conta = account_id
        self.mock_sqla.transactions_table.c.valor = last_withdrawal
        self.mock_sqla.transactions_table.c.data_transacao = transaction_date
        self.session_mock.query.return_value.filter.return_value.scalar.return_value = abs(last_withdrawal)

        limit_reached = self.mock_sqla.reached_withdrawal_limit(account_id=account_id,
                                                                withdrawal_amount=withdrawal_amount)

        self.assertTrue(limit_reached)

        self.mock_sqla.Session.assert_called_once()
        self.session_mock.query.assert_has_calls(calls=[call(self.mock_sqla.conta_table.c.limite_saque_diario),
                                                        call(mock_func.sum(
                                                            mock_func.abs(self.mock_sqla.transactions_table.c.valor)))],
                                                 any_order=True)
        self.session_mock.query.return_value.filter_by.assert_called_once_with(id_conta=account_id)
        self.session_mock.query.return_value.filter.assert_called_once_with(
            self.mock_sqla.transactions_table.c.id_conta == account_id,
            self.mock_sqla.transactions_table.c.valor < 0.0,
            self.mock_sqla.transactions_table.c.data_transacao == datetime.now().date().strftime('%Y-%m-%d')
        )

        self.session_mock.close.assert_called_once()

        withdrawal_amount = 1.0
        limit_reached = self.mock_sqla.reached_withdrawal_limit(account_id=account_id,
                                                                withdrawal_amount=withdrawal_amount)
        self.assertFalse(limit_reached)

    def test_get_account(self):
        account_id = 1
        person_id = 1
        balance = 100.00
        withdrawal_limit = 1000.0
        active_flag = True
        account_type = 1
        creation_date = datetime.now().date()
        expected_password = 'a strong password'

        expected_account = Account.from_dict({
            "id_conta": account_id,
            "id_pessoa": person_id,
            "saldo": balance,
            "limite_saque_diario": withdrawal_limit,
            "flag_ativo": active_flag,
            "tipo_conta": account_type,
            "data_criacao": creation_date.strftime('%Y-%m-%d'),
        })

        self.session_mock.query.return_value.filter_by.return_value.first.return_value = tuple(
            [account_id, person_id, balance, withdrawal_limit,
             active_flag, account_type, creation_date, expected_password]
        )

        account, password = self.mock_sqla.get_account(account_id=account_id)

        self.assertEqual(expected_password, password)
        self.assertEqual(expected_account, account)

        self.mock_sqla.Session.assert_called_once()
        self.session_mock.query.assert_called_once_with(self.mock_sqla.conta_table)
        self.session_mock.query.return_value.filter_by.assert_called_once_with(id_conta=account_id)
        self.session_mock.query.return_value.filter_by.return_value.first.assert_called_once()

        self.session_mock.close.assert_called_once()

    def test_get_account_invalid_account(self):
        account_id = 12345
        self.session_mock.query.return_value.filter_by.return_value.first.return_value = None
        account, password = self.mock_sqla.get_account(account_id=account_id)

        self.assertIsNone(account)

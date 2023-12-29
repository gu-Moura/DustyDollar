from datetime import datetime

import pytest
import unittest

from src.exceptions import InvalidOperationException
from src.models import entities
from src.models.entities import AccountType


class TestEntities(unittest.TestCase):
    def test_person_from_dict(self):
        person_dict = {
            "id_pessoa": 1,
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": "1999-01-01"
        }
        person = entities.Person.from_dict(person_dict)
        self.assertEqual(type(person), entities.Person)
        self.assertEqual(person.id_pessoa, 1)
        self.assertEqual(person.nome, "Fulano da Silva")
        self.assertEqual(person.cpf, "00000000000")
        self.assertEqual(person.data_nascimento,
                         datetime.strptime("1999-01-01", "%Y-%m-%d").date())

    def test_person_from_dict_without_id(self):
        person_dict = {
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": "1999-01-01"
        }
        person = entities.Person.from_dict(person_dict)
        self.assertIsNone(person.id_pessoa)

    def test_person_from_dict_invalid_id_exception(self):
        person_dict = {
            "id_pessoa": "ciclano",
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": "1999-01-01"
        }
        self.assertRaises(ValueError, entities.Person.from_dict, person_dict)

    def test_person_from_dict_invalid_date_exception(self):
        person_dict = {
            "id_pessoa": 1,
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": None
        }
        self.assertRaises(TypeError, entities.Person.from_dict, person_dict)

        person_dict = {
            "id_pessoa": 1,
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": 1284615
        }
        self.assertRaises(TypeError, entities.Person.from_dict, person_dict)

    def test_person_to_dict(self):
        person_dict = {
            "id_pessoa": 1,
            "nome": "Fulano da Silva",
            "cpf": "00000000000",
            "data_nascimento": "1999-01-01"
        }
        person = entities.Person.from_dict(person_dict)
        self.assertDictEqual(person.to_dict(), person_dict)

    def test_transaction_from_dict(self):
        transaction_dict = {
            "id_transacao": 1,
            "id_conta": 1,
            "valor": 100,
            "data_transacao": "2023-12-12"
        }
        transaction = entities.Transaction.from_dict(transaction_dict)
        self.assertEqual(type(transaction), entities.Transaction)
        self.assertEqual(transaction.id_conta, 1)
        self.assertEqual(transaction.id_transacao, 1)
        self.assertEqual(transaction.valor, 100)
        self.assertEqual(transaction.data_transacao,
                         datetime.strptime("2023-12-12", '%Y-%m-%d').date())

    def test_transaction_to_dict(self):
        transaction_dict = {
            "id_transacao": 1,
            "id_conta": 1,
            "valor": 100,
            "data_transacao": "2023-12-12"
        }
        transaction = entities.Transaction.from_dict(transaction_dict)
        self.assertDictEqual(transaction.to_dict(), transaction_dict)

    def test_transaction_from_dict_invalid_data(self):
        transaction_dict = {
            "id_transacao": "a",
            "id_conta": 1,
            "valor": 100,
            "data_transacao": "2023-12-12"
        }
        self.assertRaises(ValueError, entities.Transaction.from_dict, transaction_dict)

        transaction_dict = {
            "id_transacao": 1,
            "id_conta": "b",
            "valor": 100,
            "data_transacao": "2023-12-12"
        }
        self.assertRaises(ValueError, entities.Transaction.from_dict, transaction_dict)

        transaction_dict = {
            "id_transacao": 1,
            "id_conta": 1,
            "valor": "c",
            "data_transacao": "2023-12-12"
        }
        self.assertRaises(ValueError, entities.Transaction.from_dict, transaction_dict)

        transaction_dict = {
            "id_transacao": 1,
            "id_conta": 1,
            "valor": 100,
            "data_transacao": 20231212
        }
        self.assertRaises(TypeError, entities.Transaction.from_dict, transaction_dict)

    def test_account_from_dict(self):
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
        self.assertEqual(type(account), entities.Account)
        self.assertEqual(account.id_conta, 1)
        self.assertEqual(account.id_pessoa, 1)
        self.assertEqual(account.saldo, 100.0)
        self.assertEqual(account.limite_saque_diario, 1000.0)
        self.assertEqual(account.flag_ativo, True)
        self.assertEqual(account.tipo_conta.name, "Checking")
        self.assertEqual(account.tipo_conta.value, 1)
        self.assertEqual(account.data_criacao, datetime.strptime("2022-06-18", '%Y-%m-%d').date())

    def test_account_to_dict(self):
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
        self.assertDictEqual(account.to_dict(), account_dict)

    def test_account_from_dict_invalid_data_exception(self):
        account_dict = {
            "id_conta": "One",
            "id_pessoa": 1,
            "saldo": 100.0,
            "limite_saque_diario": 1000,
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": "2022-06-18",
        }
        self.assertRaises(ValueError, entities.Account.from_dict, account_dict)

        account_dict = {
            "id_conta": 1,
            "id_pessoa": "One",
            "saldo": 100.0,
            "limite_saque_diario": 1000,
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": "2022-06-18",
        }
        self.assertRaises(ValueError, entities.Account.from_dict, account_dict)

        account_dict = {
            "id_conta": 1,
            "id_pessoa": 1,
            "saldo": "One hundred",
            "limite_saque_diario": 1000,
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": "2022-06-18",
        }
        self.assertRaises(ValueError, entities.Account.from_dict, account_dict)

        account_dict = {
            "id_conta": 1,
            "id_pessoa": 1,
            "saldo": 100.0,
            "limite_saque_diario": "One thousand",
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": "2022-06-18",
        }
        self.assertRaises(ValueError, entities.Account.from_dict, account_dict)

        account_dict = {
            "id_conta": 1,
            "id_pessoa": 1,
            "saldo": 100.0,
            "limite_saque_diario": 1000,
            "flag_ativo": True,
            "tipo_conta": 3,
            "data_criacao": "2022-06-18",
        }
        self.assertRaises(ValueError, entities.Account.from_dict, account_dict)

        account_dict = {
            "id_conta": 1,
            "id_pessoa": 1,
            "saldo": 100.0,
            "limite_saque_diario": 1000,
            "flag_ativo": True,
            "tipo_conta": 1,
            "data_criacao": 20220618,
        }
        self.assertRaises(TypeError, entities.Account.from_dict, account_dict)

    def test_operation_dto_from_dict(self):
        operation_dict = {
            "account_id": 1,
            "amount": 100.0,
            "operation_type": "Deposit"
        }
        operation_dto = entities.OperationDTO.from_dict(operation_dict)
        self.assertEqual(type(operation_dto), entities.OperationDTO)
        self.assertEqual(operation_dto.account_id, 1)
        self.assertEqual(operation_dto.amount, 100.0)
        self.assertEqual(operation_dto.operation_type.name, "Deposit")
        self.assertEqual(operation_dto.operation_type.value, 1)

    def test_operation_dto_to_dict(self):
        operation_dict = {
            "account_id": 1,
            "amount": 100.0,
            "operation_type": "Deposit"
        }
        operation_dto = entities.OperationDTO.from_dict(operation_dict)
        self.assertDictEqual(operation_dto.to_dict(), operation_dict)

    def test_operation_dto_from_dict_invalid_data_exception(self):
        operation_dict = {
            "account_id": "One",
            "amount": 100.0,
            "operation_type": "Deposit"
        }
        self.assertRaises(ValueError, entities.OperationDTO.from_dict, operation_dict)

        operation_dict = {
            "account_id": 1,
            "amount": "One Hundred",
            "operation_type": "Deposit"
        }
        self.assertRaises(ValueError, entities.OperationDTO.from_dict, operation_dict)

        operation_dict = {
            "account_id": 1,
            "amount": 100.0,
            "operation_type": "Operacao Invalida"
        }
        self.assertRaises(InvalidOperationException, entities.OperationDTO.from_dict, operation_dict)

    def test_account_status_dto_from_dict(self):
        account_status_dict = {
            "account_id": 1,
            "account_active": True
        }
        account_status_dto = entities.AccountStatusDTO.from_dict(account_status_dict)
        self.assertEqual(type(account_status_dto), entities.AccountStatusDTO)
        self.assertEqual(account_status_dto.account_id, 1)
        self.assertEqual(account_status_dto.active, True)

    def test_account_status_dto_to_dict(self):
        account_status_dict = {
            "account_id": 1,
            "account_active": True
        }
        account_status_dto = entities.AccountStatusDTO.from_dict(account_status_dict)
        self.assertDictEqual(account_status_dto.to_dict(), account_status_dict)

    def test_account_status_dto_from_dict_invalid_data_exception(self):
        account_status_dict = {
            "account_id": "One",
            "account_active": True
        }
        self.assertRaises(ValueError, entities.AccountStatusDTO.from_dict, account_status_dict)

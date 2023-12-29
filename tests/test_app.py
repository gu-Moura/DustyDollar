import unittest
from unittest.mock import patch, Mock

from flask_jwt_extended import create_access_token, decode_token

from src.app import app
import json

from src.exceptions import AccountRetrievalException, AccountCreationException, DepositOperationException, \
    WithdrawalOperationException
from tests.utils.mock_db_interface import MockDBInterface


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_client = app.test_client()

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.bcrypt.check_password_hash', Mock(return_value=True))
    def test_create_token(self):
        expected_account_id = 1
        expected_person_id = 1
        expected_account_type = "Checking"
        with app.app_context():
            expected_token = create_access_token(identity=1, additional_claims={
                'person_id': 1,
                'account_type': "Checking",
            })
            response = self.test_client.post('/account/login', json={
                'account_id': 1,
                'password': '123456'
            })
            res = json.loads(response.data.decode('utf-8'))
            decoded_token = decode_token(res.get('token'))

            self.assertEqual(expected_account_id, res.get('account_id'))
            self.assertEqual(expected_account_id, decoded_token.get('sub'))
            self.assertEqual(expected_person_id, decoded_token.get('person_id'))
            self.assertEqual(expected_account_type, decoded_token.get('account_type'))
            self.assertEqual(200, response.status_code)

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.bcrypt.check_password_hash', Mock(return_value=False))
    def test_create_token_invalid_password(self):
        with app.app_context():
            response = self.test_client.post('/account/login', json={
                'account_id': 1,
                'password': '123456'
            }, headers={
                'Authorization': f"Bearer {create_access_token(identity='pytest')}"
            })
            res = json.loads(response.data.decode('utf-8'))
            self.assertDictEqual({
                'status': 'error',
                'message': 'Invalid account ID and/or password! Please try again.'
            }, res)

            self.assertEqual(400, response.status_code)

    @patch('src.app.db_interface.get_account', Mock(side_effect=AccountRetrievalException("Mock Exception")))
    def test_create_token_account_retrieval_exception(self):
        response = self.test_client.post('/account/login', json={
            'account_id': 1,
            'password': '123456'
        })
        res = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual({
            'status': 'error',
            'message': "Something went wrong while retrieving account! Please try again later."
        }, res)

        self.assertEqual(500, response.status_code)

    @patch('src.app.db_interface', MockDBInterface())
    def test_acc_creation(self):
        expected_response = {
            'status': 'success',
            'message': 'Account was successfully created!',
            'account_data': {
                'data_criacao': '2023-12-23',
                'flag_ativo': True,
                'id_conta': 42,
                'id_pessoa': 100,
                'limite_saque_diario': 1000.0,
                'saldo': 0.0,
                'tipo_conta': 'Checking'
            }
        }
        response = self.test_client.post('/account/create', json={
                "id_pessoa": 100,
                "saldo": 0.0,
                "limite_saque_diario": 1000,
                "flag_ativo": True,
                "tipo_conta": 1,
                "data_criacao": "2023-12-23",
                "password": 123456
        })
        self.assertDictEqual(expected_response, response.get_json())
        self.assertEqual(200, response.status_code)

    @patch('src.app.db_interface', MockDBInterface())
    def test_acc_creation_invalid_data(self):
        expected_response = {
            'status': 'error',
            'message': 'Invalid data format! Please check the entered data and try again!'
        }
        response = self.test_client.post('/account/create', json={
            "aidi_passoe": 100,
            "saudo": 0.0,
            "litime_dawue_siarop": 1000,
            "flag_ativo": "true",
            "tipo_conta": 1,
            "data_criacao": "2023-12-23",
            "senha": 123456
        })

        self.assertDictEqual(expected_response, response.get_json())
        self.assertEqual(400, response.status_code)

    @patch('src.app.db_interface.create_new_account', Mock(side_effect=AccountCreationException("Mock Exception")))
    def test_acc_creation_account_creation_exception(self):
        expected_response = {
            'status': 'error',
            'message': 'Account could not be created! Please check the entered data and try again!'
        }
        response = self.test_client.post('/account/create', json={
                "id_pessoa": 100,
                "saldo": 0.0,
                "limite_saque_diario": 1000,
                "flag_ativo": True,
                "tipo_conta": 1,
                "data_criacao": "2023-12-23",
                "password": 123456
        })
        self.assertDictEqual(expected_response, response.get_json())
        self.assertEqual(500, response.status_code)

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.db_interface.check_account_active', Mock(return_value=True))
    def test_acc_deposit(self):
        with app.app_context():
            response = self.test_client.post('/account/deposit', json={
                'account_id': 1,
                'amount': 100.0,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(200, response.status_code)
            self.assertDictEqual({
                'status': 'success',
                'message': 'Amount of 100.0 was successfully deposited into account 1.'
            }, response.get_json())

    @patch('src.app.db_interface.check_account_active', Mock(return_value=True))
    @patch('src.app.db_interface.deposit_into_account', Mock(side_effect=DepositOperationException("Mock Exception")))
    def test_acc_deposit_exception(self):
        with app.app_context():
            response = self.test_client.post('/account/deposit', json={
                'account_id': 1,
                'amount': 100.0,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(400, response.status_code)
            self.assertDictEqual({
                'status': 'error',
                'message': 'Could not deposit the amount of 100.0 into account 1.'
            }, response.get_json())

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.db_interface.check_account_active', Mock(return_value=True))
    def test_acc_withdraw(self):
        with app.app_context():
            response = self.test_client.post('/account/withdraw', json={
                'account_id': 1,
                'amount': 100.0,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(200, response.status_code)
            self.assertDictEqual({
                'status': 'success',
                'message': 'Amount of 100.0 was successfully withdrawn from account 1.'
            }, response.get_json())

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.db_interface.check_account_active', Mock(return_value=True))
    def test_acc_withdraw_limit_reached(self):
        with app.app_context():
            response = self.test_client.post('/account/withdraw', json={
                'account_id': 1,
                'amount': 5000.0,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(423, response.status_code)
            self.assertDictEqual({
                'status': 'error',
                'message': 'You are trying to withdraw an amount the surpasses '
                           'your daily limit for the account 1.'
            }, response.get_json())

    @patch('src.app.db_interface.withdraw_from_account', Mock(side_effect=WithdrawalOperationException("Mock Exception")))
    @patch('src.app.db_interface.reached_withdrawal_limit', Mock(return_value=False))
    @patch('src.app.db_interface.check_account_active', Mock(return_value=True))
    def test_acc_withdraw_exception(self):
        with app.app_context():
            response = self.test_client.post('/account/withdraw', json={
                'account_id': 1,
                'amount': 100.0,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(400, response.status_code)
            self.assertDictEqual({
                'status': 'error',
                'message': 'Could not withdraw the amount of 100.0 from account 1.'
            }, response.get_json())

    @patch('src.app.db_interface', MockDBInterface())
    def test_acc_active_status_block_account(self):
        with app.app_context():
            response = self.test_client.patch('/account/active', json={
                'account_id': 1,
                'active': False,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(200, response.status_code)
            self.assertDictEqual({
                'status': 'success',
                'message': 'Account 1 was successfully blocked.'
            }, response.get_json())

    @patch('src.app.db_interface', MockDBInterface())
    def test_acc_active_status_unblock_account(self):
        with app.app_context():
            response = self.test_client.patch('/account/active', json={
                'account_id': 1,
                'active': True,
            }, headers={
                'Authorization': f'Bearer {create_access_token(identity="pytest")}'
            })
            self.assertEqual(200, response.status_code)
            self.assertDictEqual({
                'status': 'success',
                'message': 'Account 1 was successfully unblocked.'
            }, response.get_json())

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

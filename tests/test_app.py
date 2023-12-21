import unittest
from unittest.mock import patch, Mock

from src.app import app
import json
from tests.utils.mock_db_interface import MockDBInterface


class TestApp(unittest.TestCase):
    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.bcrypt.check_password_hash', Mock(return_value=True))
    @patch('src.app.create_access_token', Mock(return_value='token'))
    def test_create_token(self):
        response = app.test_client().post('/account/login', json={
            'account_id': 1,
            'password': '123456'
        })
        res = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual({
            'token': 'token',
            'account_id': 1
        }, res)
        self.assertEqual(200, response.status_code)

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.bcrypt.check_password_hash', Mock(return_value=False))
    @patch('src.app.create_access_token', Mock(return_value='token'))
    def test_create_token_invalid_password(self):
        response = app.test_client().post('/account/login', json={
            'account_id': 1,
            'password': '123456'
        })
        res = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual({
            'status': 'error',
            'message': 'Invalid account ID and/or password! Please try again.'
        }, res)

        self.assertEqual(400, response.status_code)

    @patch('src.app.db_interface', MockDBInterface())
    @patch('src.app.bcrypt.check_password_hash', Exception('Mock exception'))
    def test_create_token_exception(self):
        response = app.test_client().post('/account/login', json={
            'account_id': 1,
            'password': '123456'
        })
        res = json.loads(response.data.decode('utf-8'))
        self.assertDictEqual({
            'status': 'error',
            'message': "Something went wrong while retrieving account! Please try again later."
        }, res)

        self.assertEqual(500, response.status_code)
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required

from src.app_middleware import check_if_account_is_active
from src.config import app, bcrypt, db_interface
from src.exceptions import DepositOperationException, AccountCreationException, \
    AccountRetrievalException, WithdrawalOperationException, AccountStatusChangeException, InvalidCredentialsException
from src.models.entities import Account, OperationDTO, AccountStatusDTO

from src.sqlalchemy_models import Conta, Transacao, Pessoa  # for DB migration to work


@app.route('/account/login', methods=['POST'])
def create_token():
    login_data = request.get_json()
    account_id, password = login_data['account_id'], login_data['password']
    try:
        account, account_password = db_interface.get_account(account_id)
        if not bcrypt.check_password_hash(account_password, password) or account is None:
            raise InvalidCredentialsException
    except AccountRetrievalException:
        return jsonify({
            'status': 'error',
            'message': 'Something went wrong while retrieving account! Please try again later.'
        }), 500
    except InvalidCredentialsException:
        return jsonify({
            'status': 'error',
            'message': 'Invalid account ID and/or password! Please try again.'
        }), 400

    access_token = create_access_token(identity=account.id_conta, additional_claims={
        'person_id': account.id_pessoa,
        'account_type': account.tipo_conta.name,
    })

    return jsonify({'token': access_token, 'account_id': account.id_conta})


@app.route('/account/create', methods=['POST'])
def acc_creation():
    data = request.get_json()
    try:
        new_account = Account.from_dict(data)
        password = bcrypt.generate_password_hash(str(data['password'])).decode('utf-8')
        created_account = db_interface.create_new_account(new_account, password)
    except (KeyError, TypeError):
        return jsonify({
            'status': 'error',
            'message': 'Invalid data format! Please check the entered data and try again!'
        }), 400
    except AccountCreationException:
        return jsonify({
            'status': 'error',
            'message': 'Account could not be created! Please check the entered data and try again!'
        }), 500

    return jsonify({
        'status': 'success',
        'message': 'Account was successfully created!',
        'account_data': created_account.to_dict(human_friendly=True)
    }), 200


@app.route('/account/deposit', methods=["POST"])
@jwt_required()
@check_if_account_is_active(db_interface=db_interface)
def acc_deposit():
    data = request.get_json()
    data['operation_type'] = 'Deposit'
    deposit_data = OperationDTO.from_dict(data)
    try:
        db_interface.deposit_into_account(deposit_data.account_id, deposit_data.amount)
    except DepositOperationException:
        return jsonify({
            'status': 'error',
            'message': f'Could not deposit the amount of {deposit_data.amount} into account {deposit_data.account_id}.'
        }), 400
    return jsonify({
        'status': 'success',
        'message': f'Amount of {deposit_data.amount} was successfully deposited into account {deposit_data.account_id}.'
    }), 200


@app.route('/account/withdraw', methods=["POST"])
@jwt_required()
@check_if_account_is_active(db_interface=db_interface)
def acc_withdraw():
    data = request.get_json()
    data['operation_type'] = 'Withdrawal'

    withdrawal_data = OperationDTO.from_dict(data)
    try:
        if db_interface.reached_withdrawal_limit(withdrawal_data.account_id, withdrawal_data.amount):
            return jsonify({
                'status': 'error',
                'message': "You are trying to withdraw an amount the surpasses your "
                           f"daily limit for the account {withdrawal_data.account_id}."
            }), 423

        db_interface.withdraw_from_account(withdrawal_data.account_id, withdrawal_data.amount)
    except WithdrawalOperationException:
        return jsonify({
            'status': 'error',
            'message': f'Could not withdraw the amount of {withdrawal_data.amount} '
                       f'from account {withdrawal_data.account_id}.'
        }), 400

    return jsonify({
        'status': 'success',
        'message': f'Amount of {withdrawal_data.amount} was successfully withdrawn from '
                   f'account {withdrawal_data.account_id}.'
    })


@app.route('/account/active', methods=["PATCH"])
@jwt_required()
def acc_active_status():
    data = AccountStatusDTO.from_dict(request.get_json())
    try:
        new_status = db_interface.set_account_active_status(data.account_id, data.active)
        if data.active != new_status:
            raise AccountStatusChangeException
    except AccountStatusChangeException:
        return jsonify({
            'status': 'error',
            'message': f"Couldn't {'block' if not data.active else 'unblock'} account {data.account_id}."
        }), 400
    return jsonify({
        'status': 'success',
        'message': f"Account {data.account_id} was successfully "
                   f"{'blocked' if not new_status else 'unblocked'}."
    })


@app.route('/account/balance', methods=["GET"])
@jwt_required()
@check_if_account_is_active(db_interface=db_interface)
def acc_balance():
    account_id = request.args.get('account_id', default=None, type=int)
    if account_id is None:
        return jsonify({
            'status': 'error',
            'message': 'No account_id provided.'
        }), 400

    balance = db_interface.get_balance(account_id)
    if balance is None:
        return jsonify({
            'status': 'error',
            'message': f'No account found with id {account_id}.'
        }), 404

    return jsonify({
        'status': 'success',
        'message': f"Balance of account {account_id} was retrieved successfully",
        'balance': balance
    }), 200


@app.route('/account/statement', methods=["GET"])
@jwt_required()
@check_if_account_is_active(db_interface=db_interface)
def acc_statement():
    account_id = request.args.get('account_id', default=None, type=int)
    if account_id is None:
        return jsonify({
            'status': 'error',
            'message': 'No account_id provided.'
        }), 400

    statement = [transaction.to_dict() for transaction in db_interface.get_statement_from_account(account_id)]

    return jsonify({
        "status": "success",
        "message": f"The bank statement was successfully extracted for account {account_id}",
        "bank_statement": statement
    })


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({
        'status': 'error',
        'message': str(e)
    }), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        'status': 'error',
        'message': str(e)
    }), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        'status': 'error',
        'message': str(e)
    }), 400

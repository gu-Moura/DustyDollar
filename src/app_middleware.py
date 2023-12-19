from functools import wraps

from flask import request, jsonify
from services.ports.db_interface import DBInterface


def check_if_account_is_active(db_interface: DBInterface):
    def actual_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == "GET":
                account_id = request.args.get('account_id', default=None, type=int)
            else:
                account_id = int(request.get_json().get('account_id'))
            if not db_interface.check_account_active(account_id):
                return jsonify({
                    'status': 'error',
                    'message': f'Account {account_id} is currently blocked and you cannot make any operations with it.'
                }), 400
            result = f(*args, **kwargs)
            return result
        return decorated_function
    return actual_decorator

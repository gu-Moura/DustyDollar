from config import app
from models import Conta, Transacao, Pessoa


@app.route('/')
def hello_world():  # put application's code here
    return "Welcome to bank"


@app.route('/account/create', methods=['POST'])
def acc_creation():
    ...


@app.route('/account/login', methods=['POST'])
def acc_login():
    ...


@app.route('/account/deposit', methods=["POST"])
def acc_deposit():
    ...


@app.route('/account/withdraw', methods=["POST"])
def acc_withdraw():
    ...


@app.route('/account/block', methods=["PATCH"])
def acc_block():
    ...


@app.route('/account/balance', methods=["GET"])
def acc_balance():
    ...


@app.route('/account/statement', methods=["GET"])
def acc_statement():
    ...



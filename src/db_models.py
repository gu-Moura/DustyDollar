from src.config import db


class Conta(db.Model):
    id_conta = db.Column(db.Integer, primary_key=True, nullable=False)
    id_pessoa = db.Column(db.Integer, nullable=False)
    senha = db.Column(db.Text, nullable=False)
    saldo = db.Column(db.DECIMAL(10, 2), default=0.0)
    limite_saque_diario = db.Column(db.DECIMAL(10, 2), default=1000.0)
    flag_ativo = db.Column(db.Boolean, default=True)
    tipo_conta = db.Column(db.Integer, nullable=False)
    data_criacao = db.Column(db.Date, nullable=False)


class Transacao(db.Model):
    id_transacao = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    id_conta = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.DECIMAL(10, 2), nullable=False)
    data_transacao = db.Column(db.Date, nullable=False)


class Pessoa(db.Model):
    id_pessoa = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = db.Column(db.Text(), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)

from config import db


class Conta(db.Model):
    id_conta = db.Column(db.Integer, primary_key=True)
    id_pessoa = db.Column(db.Integer)
    saldo = db.Column(db.Numeric)
    limite_saque_diario = db.Column(db.Numeric)
    flag_ativo = db.Column(db.Boolean, default=True)
    tipo_conta = db.Column(db.Numeric)
    data_criacao = db.Column(db.Date)


class Transacao(db.Model):
    id_transacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_conta = db.Column(db.Integer)
    valor = db.Column(db.Numeric)
    data_transacao = db.Column(db.Date)


class Pessoa(db.Model):
    id_pessoa = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = db.Column(db.Text())
    cpf = db.Column(db.String(11))
    data_nascimento = db.Column(db.Date)

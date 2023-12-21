from faker import Faker
import random
from src.models.entities import Person, Account, Transaction
import src.services.db_service as sqla

fake = Faker("pt_BR")


def generate_transaction(acc_id: int, transaction_id: int) -> Transaction:
    transaction = {
        'id_transacao': transaction_id,
        'id_conta': acc_id,
        'valor': random.random() * 10000 - 5000,
        'data_transacao': fake.date()
    }
    return Transaction.from_dict(transaction)


def generate_conta(id_pessoa: int = -1) -> Account:
    account = {
        'id_conta': fake.aba(),
        'id_pessoa': id_pessoa,
        'saldo': random.random() * 10000 - 5000,
        'limite_saque_diario': random.random() * 10000,
        'flag_ativo': True,
        'tipo_conta': 1,
        'data_criacao': fake.date()
    }
    return Account.from_dict(account)


def generate_person(pid: int) -> Person:
    person = {
        "id_pessoa": pid,
        "nome": fake.name(),
        "cpf": fake.cpf().replace('.', '').replace('-', ''),
        "data_nascimento": fake.date_of_birth().strftime("%Y-%m-%d")
    }
    return Person.from_dict(person)


def populate_database():
    pessoas = [generate_person(i + 1) for i in range(125)]
    contas = [generate_conta() for _ in range(250)]
    transacoes = [generate_transaction(acc_id=-1, transaction_id=i) for i in range(5000)]

    for pessoa in pessoas:
        sqla.create_new_person(pessoa)

    for conta in contas:
        conta.id_pessoa = random.choice(pessoas).id_pessoa
        sqla.create_new_account(conta)

    for transacao in transacoes:
        transacao.id_conta = random.choice(contas).id_conta
        sqla.make_transaction(transacao.id_conta, transacao.valor)

    print("Done")


if __name__ == '__main__':
    populate_database()
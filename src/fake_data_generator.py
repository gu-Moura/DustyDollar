from faker import Faker
import random
from models.entities import Pessoa, Conta, Transacao

fake = Faker("pt_BR")


def generate_transaction(acc_id: int, transaction_id: int) -> Transacao:
    transaction = {
        'id_transacao': transaction_id,
        'id_conta': acc_id,
        'valor': random.random() * 10000 - 5000,
        'data_transacao': fake.date()
    }
    return Transacao.from_dict(transaction)


def generate_conta(id_pessoa: int = -1) -> Conta:
    account = {
        'id_conta': fake.aba(),
        'id_pessoa': id_pessoa,
        'saldo': random.random() * 10000 - 5000,
        'limite_saque_diario': random.random() * 10000,
        'flag_ativo': random.random() > 0.5,
        'tipo_conta': random.randint(0, 3),
        'data_criacao': fake.date()
    }
    return Conta.from_dict(account)


def generate_person(pid: int) -> Pessoa:
    person = {
        "id_pessoa": pid,
        "nome": fake.name(),
        "cpf": fake.cpf(),
        "data_nascimento": fake.date_of_birth().strftime("%Y-%m-%d")
    }
    return Pessoa.from_dict(person)



def populate_database():
    pessoas = [generate_person(i) for i in range(125)]
    contas = [generate_conta() for _ in range(250)]
    transacoes = [generate_transaction(acc_id=-1, transaction_id=i) for i in range(5000)]

    for conta in contas:
        conta.id_pessoa = random.choice(pessoas).id_pessoa

    for transacao in transacoes:
        transacao.id_conta = random.choice(contas).id_conta

    print("Done")


if __name__ == '__main__':
    populate_database()
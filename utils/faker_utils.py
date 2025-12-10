from faker import Faker
import random

fake = Faker()


def random_person():
    return {
        'name': fake.name(),
        'email': fake.email(),
        'username': fake.user_name(),
        'age': random.randint(0, 130)
    }


def random_text(paragraphs=1):
    return '\n'.join(fake.paragraph() for _ in range(paragraphs))
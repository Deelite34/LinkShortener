import random
import string


def random_sequence(length):
    return ''.join(random.choice(string.ascii_letters) for _ in length)
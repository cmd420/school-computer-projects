import random


def random_str(length: int = 6) -> str:
    ret = ''
    alphabets = 'abcdefghijklmnopqrstuvwxyz0123456789'

    for _ in range(length):
        ret += random.choice(alphabets)

    return ret

def get_ext(url: str) -> str:
    tokens = url.split('.')
    return tokens[-1]

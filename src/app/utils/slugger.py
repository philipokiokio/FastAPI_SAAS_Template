from uuid import uuid4


def slug_gen() -> str:
    return uuid4().hex

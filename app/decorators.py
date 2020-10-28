from app.config import session


def commit_transaction(func):
    def wrapped(self):
        func(self)
        session.commit()

    return wrapped

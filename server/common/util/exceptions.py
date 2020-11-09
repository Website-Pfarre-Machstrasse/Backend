class AuthorisationError(Exception):
    pass


class UserNotFoundError(Exception):
    def __init__(self, identity):
        self.identity = identity

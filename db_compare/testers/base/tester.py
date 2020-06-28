from abc import abstractmethod
from argparse import ArgumentParser
from subprocess import PIPE, check_call
from typing import List

from db_compare.util import User


class Tester:
    def __init__(self, args):
        self.args = args

    @staticmethod
    def run(*args, quiet=False):
        if len(args) == 1 and ' ' in args[0]:
            args = tuple(args[0].split())
        kwargs = {'stdout': PIPE, 'stderr': PIPE} if quiet else {}
        return check_call(args, **kwargs)

    @staticmethod
    def add_parser_args(parser: ArgumentParser):
        pass

    # === Abstract Methods ===

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def insert_one(self, user: User):
        pass

    def insert_many(self, users: List[User]):
        for i in users:
            self.insert_one(i)

    @abstractmethod
    def get_saved_emails(self):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    def cleanup(self):
        pass

    insert_many.is_default = True
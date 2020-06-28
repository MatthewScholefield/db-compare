from abc import abstractmethod
from typing import List

from lazy import lazy

from db_compare.util import User
from db_compare.testers.base.tester import Tester


class PeweeTester(Tester):
    @abstractmethod
    def get_db(self):
        pass

    def __init__(self, args):
        super().__init__(args)
        self.__user = User
        self.ensure_running()
        self.has_started = False

    @abstractmethod
    def ensure_running(self):
        pass

    @lazy
    def db(self):
        _ = self.user
        return self.db

    @lazy
    def user(self):
        from peewee import Model, CharField
        self.db = self.get_db()
        self.has_started = True

        class User(Model):
            name = CharField(40)
            email = CharField(60, unique=True)
            passwordHash = CharField(120)
            about = CharField(512)

            class Meta:
                database = self.db

        self.db.connect()
        return User

    def insert_many(self, users: List[User]):
        self.user.insert_many([user._asdict() for user in users]).execute()

    def insert_one(self, user: User):
        self.user.insert(user._asdict()).execute()

    def get_saved_emails(self):
        return [i.email for i in self.user.select(self.user.email)]
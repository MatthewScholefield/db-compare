import atexit
import os
from _signal import SIGINT
from subprocess import Popen
from time import sleep

from db_compare.util import User
from db_compare.testers.base.tester import Tester


class RukoTester(Tester):
    def __init__(self, args):
        super().__init__(args)
        self.db = self.connect()
        self.users = self.db['dbtest']

    def setup(self):
        self.users[()] = []
        self.users.by('email').get('')

    def insert_one(self, user: User):
        self.users.append(dict(user._asdict()))

    def get_saved_emails(self):
        return [i['email'] for i in self.users()]

    def get_user_by_email(self, email: str) -> User:
        return User(**self.users.by('email')[email]())

    def cleanup(self):
        del self.users[()]

    @staticmethod
    def connect():
        p = Popen(['ruko-server'])
        atexit.register(lambda: os.kill(p.pid, SIGINT))
        sleep(2.0)
        from ruko import RDict
        db = RDict.client()
        try:
            db['ping'] = True
        except Exception as e:
            print(
                'Error: Ruko failed to connect. Make sure redis-server is installed and not already running ({})'.format(
                    e))
            raise SystemExit(1)
        return db
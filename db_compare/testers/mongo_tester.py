from subprocess import check_call
from time import sleep
from typing import List

from db_compare.util import User
from db_compare.testers.base.tester import Tester


class MongoTester(Tester):
    def setup(self):
        pass

    def __init__(self, args):
        super().__init__(args)
        self.client = self.get_client()
        from pymongo.write_concern import WriteConcern
        from pymongo import IndexModel

        from pymodm import MongoModel, fields

        class UserModel(MongoModel):
            name = fields.CharField(max_length=40)
            email = fields.CharField(max_length=60)
            passwordHash = fields.CharField(max_length=120)
            about = fields.CharField(max_length=512)

            class Meta:
                write_concern = WriteConcern(j=True)
                indexes = [IndexModel([('email', 1)])]

        self.user = UserModel

    def insert_one(self, user: User):
        self.user(**user._asdict()).save()

    def insert_many(self, users: List[User]):
        self.user.objects.bulk_create([
            self.user(**i._asdict())
            for i in users
        ])

    def get_saved_emails(self):
        return [i['email'] for i in self.client.dbtest.user_model.find({}, {'email': 1, '_id': 0})]

    def get_user_by_email(self, email: str) -> User:
        user = self.user.objects.raw({'email': email})[0]
        return User(name=user.name, email=user.email, passwordHash=user.passwordHash, about=user.about)

    def cleanup(self):
        self.client.drop_database('dbtest')

    def get_client(self, retry=True):
        from pymodm.connection import connect
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        dburl = "mongodb://localhost:27017/dbtest"
        client = MongoClient(host=[dburl], serverSelectionTimeoutMS=200)
        try:
            client.server_info()
            connect(dburl)
            return client
        except ServerSelectionTimeoutError:
            if not retry:
                raise
            check_call('sudo systemctl start mongodb'.split())
            sleep(1.0)
            return self.get_client(False)
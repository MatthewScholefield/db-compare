from subprocess import call, PIPE, check_call
from typing import List

from lazy import lazy

from db_compare.util import User
from db_compare.testers.base.tester import Tester


class MariadbTester(Tester):
    def __init__(self, args):
        super().__init__(args)
        self.ensure_started()
        self.has_started = False

    @lazy
    def db(self):
        self.has_started = True
        return self.connect()

    def run_root_mysql(self, command: str):
        self.run('sudo', 'mysql', '--execute', command)

    def setup(self):
        self.run_root_mysql('CREATE DATABASE IF NOT EXISTS dbtest;')
        self.run_root_mysql("CREATE USER IF NOT EXISTS 'dbtest'@'localhost' IDENTIFIED BY 'dbtest';")
        self.run_root_mysql("GRANT ALL PRIVILEGES ON dbtest . * TO 'dbtest'@'localhost'")
        c = self.db.cursor()
        c.execute('''
            CREATE TABLE Account(
                id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                email VARCHAR(60) NOT NULL UNIQUE,
                passwordHash VARCHAR(120) NOT NULL,
                about VARCHAR(512) NOT NULL,
                permissions INT NOT NULL DEFAULT 0b01
            )
        ''')

    def insert_many(self, users: List[User]):
        self.db.cursor().executemany(
            'INSERT INTO Account (name, email, passwordHash, about) VALUES (%s, %s, %s, %s)',
            [(i.name, i.email, i.passwordHash, i.about) for i in users]
        )
        self.db.commit()

    def insert_one(self, user: User):
        self.db.cursor().executemany(
            'INSERT INTO Account (name, email, passwordHash, about) VALUES (%s, %s, %s, %s)',
            (user.name, user.email, user.passwordHash, user.about)
        )
        self.db.commit()

    def get_saved_emails(self):
        c = self.db.cursor()
        c.execute('SELECT email FROM Account')
        return [email for email, in c.fetchall()]

    def get_user_by_email(self, email: str) -> User:
        c = self.db.cursor()
        c.execute('SELECT name, email, passwordHash, about FROM Account WHERE email = %s', (email,))
        name, email, passwordHash, about = c.fetchone()
        return User(name=name, email=email, passwordHash=passwordHash, about=about)

    def cleanup(self):
        if self.has_started:
            self.db.close()
        self.run_root_mysql('DROP DATABASE IF EXISTS dbtest;')
        self.run_root_mysql('DROP USER IF EXISTS dbtest;')

    @staticmethod
    def ensure_started():
        if call(['mysql', '--execute', 'SELECT 1;'], stdout=PIPE, stderr=PIPE) != 0:
            check_call(['sudo', 'systemctl', 'start', 'mariadb'])

    @staticmethod
    def connect():
        import MySQLdb
        db = MySQLdb.connect("localhost", "dbtest", "dbtest", "dbtest")
        db.autocommit(False)
        return db
from db_compare.util import User
from db_compare.testers.base.pewee_tester import PeweeTester


class MariadbPeweeTester(PeweeTester):
    def get_db(self):
        import peewee
        return peewee.MySQLDatabase('dbtest', user='dbtest', password='dbtest')

    def ensure_running(self):
        try:
            self.run_mysql('SELECT 1', quiet=True)
        except Exception:
            self.run('sudo', 'systemctl', 'start', 'mariadb')

    def run_mysql(self, command: str, quiet=False):
        self.run('sudo', 'mysql', '--execute', command, quiet=quiet)

    def setup(self):
        self.run_mysql('CREATE DATABASE IF NOT EXISTS dbtest;')
        self.run_mysql("CREATE USER IF NOT EXISTS 'dbtest'@'localhost' IDENTIFIED BY 'dbtest';")
        self.run_mysql("GRANT ALL PRIVILEGES ON dbtest . * TO 'dbtest'@'localhost'")
        self.db.create_tables([self.user])

    def cleanup(self):
        if self.has_started:
            self.db.close()
        self.run_mysql("DROP DATABASE IF EXISTS dbtest")
        self.run_mysql("DROP USER IF EXISTS dbtest")

    def get_user_by_email(self, email: str) -> User:
        user = self.user.get(self.user.email == email)
        return User(name=user.name, email=user.email, passwordHash=user.passwordHash, about=user.about)
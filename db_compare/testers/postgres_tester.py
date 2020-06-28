from db_compare.util import User
from db_compare.testers.base.pewee_tester import PeweeTester


class PostgresTester(PeweeTester):
    def get_db(self):
        import peewee
        return peewee.PostgresqlDatabase('dbtest', user='dbtest', password='dbtest')

    def ensure_running(self):
        try:
            self.run_psql('SELECT 1')
        except Exception:
            self.run('sudo', 'systemctl', 'start', 'postgresql')

    def run_psql(self, command: str):
        self.run('sudo', '-u', 'postgres', 'psql', '-c', command, quiet=True)

    def setup(self):
        self.run_psql("CREATE DATABASE dbtest")
        self.run_psql("CREATE USER dbtest WITH PASSWORD 'dbtest'")
        self.run_psql('GRANT ALL PRIVILEGES ON DATABASE "dbtest" to dbtest')
        self.db.create_tables([self.user])

    def cleanup(self):
        if self.has_started:
            self.db.close()
        self.run_psql("DROP DATABASE IF EXISTS dbtest")
        self.run_psql("DROP USER IF EXISTS dbtest")

    def get_user_by_email(self, email: str) -> User:
        c = self.db.execute_sql(
            'SELECT "name", "email", "passwordHash", "about" FROM "user" WHERE "email" = %s',
            (email,), commit=False
        )
        name, email, passwordHash, about = c.fetchone()
        return User(name=name, email=email, passwordHash=passwordHash, about=about)
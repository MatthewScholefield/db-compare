import atexit
import os
from _signal import SIGINT
from argparse import ArgumentParser
from subprocess import check_call, Popen
from time import sleep

from db_compare.util import User
from db_compare.testers.base.tester import Tester


class RedisGraphTester(Tester):
    def __init__(self, args):
        super().__init__(args)
        import redis
        from redisgraph import Graph
        self.red = redis.Redis()
        self.redis_graph = Graph('dbtest', self.red)
        self.start_server()

    @staticmethod
    def add_parser_args(parser: ArgumentParser):
        parser.add_argument('--so-path', required=True, help='.so file from compiled redis-server')

    def setup(self):
        pass

    def insert_one(self, user: User):
        query = "CREATE (p:Person { name: $name, email: $email, passwordHash: $passwordHash, about: $about })"
        self.redis_graph.query(query, dict(user._asdict()))

    def get_saved_emails(self):
        return [i[0] for i in self.redis_graph.query('MATCH (p:Person) RETURN p.email').result_set]

    def get_user_by_email(self, email: str) -> User:
        query_result = self.redis_graph.query(
            'MATCH (p:Person { email: $email }) RETURN p',
            dict(email=email)
        )
        return User(**query_result.result_set[0][0].properties)

    def cleanup(self):
        check_call(['rm', '-f', 'dump.rdb'])

    def start_server(self):
        p = Popen(['redis-server', '--loadmodule', str(self.args.so_path)])
        atexit.register(lambda: os.kill(p.pid, SIGINT))
        sleep(0.5)
        try:
            self.red.ping()
        except Exception:
            print('Error: Redis failed to connect. Make sure redis-server is installed and not already running')
            raise SystemExit(1)
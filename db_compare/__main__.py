import random
from argparse import ArgumentParser, Namespace
from time import time, sleep
from typing import Dict
from typing import Type

import plotille

from db_compare.testers.base.tester import Tester
from db_compare.testers.mariadb_pewee_tester import MariadbPeweeTester
from db_compare.testers.mariadb_tester import MariadbTester
from db_compare.testers.mongo_tester import MongoTester
from db_compare.testers.postgres_tester import PostgresTester
from db_compare.testers.redis_graph_tester import RedisGraphTester
from db_compare.testers.ruko_tester import RukoTester
from db_compare.util import rand_string, rand_dist_string, User

testers = {
    'mariadb': MariadbTester,
    'redis-graph': RedisGraphTester,
    'ruko': RukoTester,
    'mongo': MongoTester,
    'postgres': PostgresTester,
    'mariadb-pewee': MariadbPeweeTester
}  # type: Dict[str, Type[Tester]]


def run_test(tester: Tester, args: Namespace):
    if 'setup' in args.stages:
        print('Cleaning database...')
        tester.cleanup()
        print('Setting up database...')
        tester.setup()

    if 'insert' in args.stages:
        print('Generating {} users...'.format(args.num_users))
        users = [
            User(
                name=rand_dist_string(40),
                email=rand_dist_string(60),
                passwordHash=rand_string(120),
                about=rand_dist_string(512, power=4)
            )
            for _ in range(args.num_users)
        ]
        print('Inserting {} users...'.format(args.num_users))
        tester.insert_many(users)

    if 'retrieve' in args.stages:
        print('Fetching all saved emails...')
        emails = tester.get_saved_emails()
        print('Fetched {} emails.'.format(len(emails)))

        sleep(2.0)

        print('Fetching {} random emails...'.format(args.num_tests))
        times = []
        for i in range(args.num_tests):
            email = random.choice(emails)
            start = time()
            tester.get_user_by_email(email)
            end = time()
            times.append(1000 * (end - start))

        times.sort()
        print()
        print(plotille.hist(times[int(len(times) * 0.1):int(len(times) * 0.9)], bins=args.histogram_rows))
        print()
        print('Average: {}ms, Min: {}ms, Max: {}ms'.format(
            sum(times) / len(times), min(times), max(times)
        ))


def main():
    parser = ArgumentParser(description='')
    parser.add_argument('-n', '--num-users', default=10_000, type=int)
    parser.add_argument('-t', '--num-tests', default=4_000, type=int)
    parser.add_argument('-s', '--stage', action='append', default=[])
    parser.add_argument('-ns', '--no-stage', action='append', default=[])
    parser.add_argument('-hr', '--histogram-rows', default=15, type=int)
    subparsers = parser.add_subparsers(dest='db_name')
    subparsers.required = True

    for name, tester in testers.items():
        subparser = subparsers.add_parser(name)
        tester.add_parser_args(subparser)

    args = parser.parse_args()
    args.stages = set(args.stage or ['setup', 'insert', 'retrieve', 'cleanup']) - set(args.no_stage)
    del args.stage
    del args.no_stage
    tester = testers[args.db_name](args)

    try:
        run_test(tester, args)
    finally:
        if 'cleanup' in args.stages:
            print('')
            tester.cleanup()


if __name__ == '__main__':
    main()

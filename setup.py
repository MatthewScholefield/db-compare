from setuptools import setup

setup(
    name='db-compare',
    version='0.1.0',
    description='A small scale apples-to-oranges database benchmark',
    url='https://github.com/MatthewScholefield/db-compare',
    author='Matthew D. Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='db compare',
    packages=['db_compare'],
    install_requires=[
        'mysqlclient',
        'redisgraph',
        'redis',
        'plotille',
        'ruko',
        'pymodm',
        'pymongo',
        'lazy',
        'peewee',
        'psycopg2'
    ],
    entry_points={
        'console_scripts': [
            'db-compare=db_compare.__main__:main'
        ],
    }
)

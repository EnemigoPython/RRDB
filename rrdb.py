import os
import sqlite3
from dotenv import load_dotenv
from argparse import ArgumentParser

def sql_query(text: str, *params):
    cur = con.cursor()
    res = cur.execute(text, params)
    con.commit()
    return list(res)

def init(*_):
    print("init !")

def save():
    print("save !")

def query():
    print("query !")

def main():
    load_dotenv()
    global con
    con = sqlite3.connect(os.getenv('DB_PATH'))
    parser = ArgumentParser(prog='RRDB')
    subparsers = parser.add_subparsers()
    subparsers.required = True

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)
    parser_save = subparsers.add_parser('save')
    parser_save.set_defaults(func=save)
    parser_query = subparsers.add_parser('query')
    parser_query.set_defaults(func=query)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

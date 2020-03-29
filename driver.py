import os
import sys
from argparse import ArgumentParser
from argparse import FileType
from pw.db import create_db_instance
from pw.db import validate_db

db = create_db_instance()
conn = db.conn
cur = db.cur

cur.execute("""create table if not exists test(
            app text PRIMARY KEY,
            user text,
            password text,
            createtime text not null,
            updatetime text not null DEFAULT (datetime('now','localtime'))
            )""")

def validate_pw(pw):
    if len(pw)>8:
        return pw
    raise ValueError("password needs to be longer than 8 characters")

def format_cursor_results(cur, columns=False):
    data = cur.fetchall()
    if columns:
        cols = [i[0] for i in cur.description]
        data = [cols, *data]
    return "\r\n".join(["\t".join(row) for row in data])

get_select_stmt = "select user, password from test where app = ?"

def get_pw(args):
    cur.execute(get_select_stmt,[args.app])
    print(format_cursor_results(cur))

upsert_stmt = """
            insert into test(app, user, password, createtime)
            values (?,?,?,datetime('now','localtime'))
            on conflict(app) do
            update set
            password=excluded.password,
            user=excluded.user,
            updatetime=datetime('now','localtime')
            """

def set_pw(args):
    bind = [args.app, args.user, args.password]
    cur.execute(upsert_stmt, bind)
    conn.commit()

del_stmt = "delete from test where app = ?"

def del_pw(args):
    cur.execute(del_stmt, [args.app])
    conn.commit()

def dump(args):
    if args.all_data:
        data = cur.execute("select * from test")
    else:
        data = cur.execute("select app from test")
    _ = args.file.write(format_cursor_results(cur, columns=True))

def create_parser():
    parser = ArgumentParser()
    sub = parser.add_subparsers()
    
    get_parser = sub.add_parser("get")
    get_parser.add_argument("app")
    get_parser.set_defaults(func=get_pw)
    
    set_parser = sub.add_parser("set")
    set_parser.add_argument("app")
    set_parser.add_argument("user", type=lambda x: x.lower())
    set_parser.add_argument("password", type=validate_pw)
    set_parser.set_defaults(func=set_pw)

    rm_parser = sub.add_parser("rm")
    rm_parser.add_argument("app")
    rm_parser.set_defaults(func=del_pw)
    
    list_parser = sub.add_parser("dump")
    list_parser.add_argument("-f", "--file", type=FileType("w"), default=sys.stdout)
    list_parser.add_argument("--all-data", action="store_true")
    list_parser.set_defaults(func=dump)

    #tbd:
    #suggest_parser = sub.add_parser("suggest")
    return parser

def main():
    validate_db()
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)

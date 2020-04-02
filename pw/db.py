import os
import sqlite3
from collections import OrderedDict
from enum import Enum
from functools import total_ordering


__all__ = ["get_app",
           "set_app",
           "del_app",
           "get_all",
           "InvalidDBVersion"]

CONNECTION_STR = os.path.join(os.path.dirname(__file__), "store")

def create_db_instance():
    return DB(CONNECTION_STR)

def create_pw_table_instance():
    return PasswordTable()

def get_app(app):
    db = create_db_instance()
    stmt = create_pw_table_instance().get_app_stmt()
    with db:
        db.execute(stmt, [app])
        try:
            return next(db)
        except StopIteration:
            return {"status": "empty",
                    "msg": "no results found for {!r}".format(app)}

def set_app(app, user, password):
    db = create_db_instance()
    stmt = create_pw_table_instance().set_app_stmt()
    with db:
        result = {"status": "failed"}
        try:
            with db.conn:
                db.execute(stmt, [app,user,password])
        except sqlite3.OperationalError as err:
            result["msg"] = ("unable to set password for {!r}. "
                             "ensure no other processes are running "
                             "pw concurrently" .format(app))
        except Exception as err:
            result["msg"] = "unable to set password for {!r}".format(app)
        else:
            if db.cur.rowcount == 0:
                result["status"] = "empty"
                result["msg"] = ("no updates made. "
                                 "ensure {!r} exists".format(app))
            else:
                result["status"] = "success"
        return result

def del_app(app):
    db = create_db_instance()
    stmt = create_pw_table_instance().del_app_stmt()
    with db:
        result = {"status": "failed"}
        try:
            with db.conn:
                db.execute(stmt, [app])
        except sqlite3.OperationalError as err:
            result["msg"] = ("unable to delete {!r} password. "
                             "ensure no other processes are running "
                             "pw concurrently" .format(app))
        except Exception as err:
            result["msg"] = "unable to delete {!r} password".format(app)
        else:
            if db.cur.rowcount == 0:
                result["status"] = "empty"
                result["msg"] = ("no updates made. "
                                 "ensure {!r} exists".format(app))
            else:
                result["status"] = "success"
        return result

def get_all(all_columns):
    db = create_db_instance()
    stmt = create_pw_table_instance().get_all_stmt(all_columns)
    with db:
        db.execute(stmt)
        return list(db) or [{"status": "empty",
                             "msg": "no data found"}]

def create_pw_table():
    db = create_db_instance()
    stmt = create_pw_table_instance().create_table_stmt()
    with db:
        db.execute(stmt)


class Error(Exception):
    pass


class InvalidDBVersion(Error):
    pass


class DB(object):
    def __init__(self, connect_str):
        if DBVersion.installed < DBVersion.required:
            raise InvalidDBVersion("sqlite version {} or higher "
                                   "required. installed version is "
                                   "{}".format(DBVersion.required.value,
                                               DBVersion.installed.value))
        self.conn = sqlite3.connect(connect_str)
        self.cur = self.conn.cursor()

    def execute(self, *args, **kwargs):
        try:
            return self.cur.execute(*args, **kwargs)
        except sqlite3.OperationalError as err:
            #OperationalError thrown for sql syntax errors
            #including refs to unknown tables. if this error
            #is thrown for sql syntax errors that would be a defect.
            #therefore most likely the only time this error is
            #thrown is the first sql executed when no tables exist.
            #this block catches the error, creates table, re-executes
            create_pw_table()
            return self.cur.execute(*args, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        columns = [i[0] for i in self.cur.description]
        return OrderedDict(zip(columns, next(self.cur)))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.conn.close()


class PasswordTable(object):

    name = "password"

    def create_table_stmt(self):
        return """create table if not exists {table}(
                    app text PRIMARY KEY,
                    user text,
                    password text,
                    createtime text not null,
                    updatetime text not null DEFAULT (datetime('now','localtime'))
                    )""".format(table=self.name)

    def get_app_stmt(self):
        return """select user, password
                from {table}
                where app = ?""".format(table=self.name)

    def set_app_stmt(self):
        return """
                insert into {table}(app, user, password, createtime)
                values (?,?,?,datetime('now','localtime'))
                on conflict(app) do
                update set
                password=excluded.password,
                user=excluded.user,
                updatetime=datetime('now','localtime')
                """.format(table=self.name)

    def del_app_stmt(self):
        return "delete from {table} where app = ?".format(table=self.name)

    def get_all_stmt(self, all_columns=False):
        if all_columns:
            return "select * from {table}".format(table=self.name)
        else:
            return "select app from {table}".format(table=self.name)


@total_ordering
class DBVersion(Enum):
    required = "3.24.0"
    installed = sqlite3.sqlite_version

    def __init__(self, version):
        version_split = map(int, version.split("."))
        try:
            self.major, self.minor, self.patch = version_split
        except ValueError as ve:
            raise ValueError("db version must have 3 numeric "
                             "parts: major, minor, patch")

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            if self.__eq__(other):
                return True
            elif self.major > other.major:
                return True
            elif (self.major == other.major
                  and self.minor > other.minor):
                return True
            elif (self.major == other.major
                  and self.minor == other.minor
                  and self.patch > other.patch):
                return True
            return False
        return NotImplemented

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (self.major == other.major
                    and self.minor == other.minor
                    and self.patch == other.patch)
        return NotImplemented

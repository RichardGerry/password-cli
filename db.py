import os
import sqlite3
from enum import Enum
from functools import total_ordering


__all__ = ["create_db_instance",
           "validate_db"]


CONNECTION_STR = os.path.join(os.path.dirname(__file__), "store")

def create_db_instance():
    return DB(CONNECTION_STR)

def validate_db():
    if DBVersion.installed < DBVersion.required:
        raise Exception("sqlite version {} or higher "
                        "required. installed version is "
                        "{}".format(DBVersion.required.value,
                                    DBVersion.installed.value))


class DB(object):
    def __init__(self, connect_str):
        self.conn = sqlite3.connect(connect_str)
        self.cur = self.conn.cursor()


@total_ordering
class DBVersion(Enum):
    required = "3.24.0"
    installed = sqlite3.sqlite_version

    def __init__(self, version):
        version_split = version.split(".")
        if len(version_split) < 3:
            raise ValueError("db version must have 3 parts: "
                             "major, minor, patch")
        self.major, self.minor, self.patch = version_split

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return (self.major >= other.major
                    and self.minor >= other.minor
                    and self.patch >= other.patch)
        return NotImplemented

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (self.major == other.major
                    and self.minor == other.minor
                    and self.patch == other.patch)
        return NotImplemented

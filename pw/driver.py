import os
import sys
import json
from argparse import ArgumentParser
from argparse import FileType
from argparse import ArgumentTypeError
from pw.db import get_app
from pw.db import set_app
from pw.db import del_app
from pw.db import get_all
from pw.db import InvalidDBVersion


def format_sql_result(js):
    return json.dumps(js, indent=4)

def get_pw(args):
    result = get_app(args.app)
    sys.stdout.write(format_sql_result(result))

def set_pw(args):
    result = set_app(args.app, args.user, args.password)
    sys.stdout.write(format_sql_result(result))

def del_pw(args):
    result = del_app(args.app)
    sys.stdout.write(format_sql_result(result))

def dump(args):
    data = get_all(args.all_data)
    if args.lines:
        lines = [[v for _,v in row.items()] for row in data]
        if args.all_data:
            columns = [k for k,_ in data[0].items()]
            lines = [columns, *lines]
        comma_join = ",".join
        data_str = "\r\n".join(map(comma_join, lines)) + "\n"
    else:
        data_str = "\n".join(map(format_sql_result, data))
    _ = args.file.write(data_str)

def validate_pw(pw):
    if len(pw)>8:
        return pw
    raise ArgumentTypeError("password needs to be longer than 8 characters")

def create_common_parser():
    common_parser = ArgumentParser(add_help=False)
    common_parser.add_argument("app",
                               type=lambda x: x.lower(),
                               help="application name for the user/password")
    return common_parser

def create_parser():
    parser = ArgumentParser(description=("store and retrieve application "
                                         "user names and passwords"))
    sub = parser.add_subparsers()
    common_parser = create_common_parser()
    
    get_parser = sub.add_parser("get",
                                parents=[common_parser],
                                help="retrieve an application user/password")
    get_parser.set_defaults(func=get_pw)
    
    set_parser = sub.add_parser("set",
                                parents=[common_parser],
                                help="update or add an application user/password")
    set_parser.add_argument("user",
                            type=lambda x: x.lower(),
                            help="application user name")
    set_parser.add_argument("password",
                            type=validate_pw,
                            help="application password")
    set_parser.set_defaults(func=set_pw)

    rm_parser = sub.add_parser("rm",
                               parents=[common_parser],
                               help="remove an application user/password")
    rm_parser.set_defaults(func=del_pw)
    
    list_parser = sub.add_parser("dump", help="output all applications stored")
    list_parser.add_argument("-f", "--file",
                             type=FileType("w"),
                             default=sys.stdout,
                             help="file to write the output (default is std output)")
    list_parser.add_argument("--all-data",
                             action="store_true",
                             help=("flag to output all app data stored "
                                   "(default is only output app name)"))
    list_parser.add_argument("--lines",
                             action="store_true",
                             help=("flag to output data in csv format "
                                   "(default is json)"))
    list_parser.set_defaults(func=dump)

    #tbd:
    #suggest_parser = sub.add_parser("suggest")
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except InvalidDBVersion as err:
        sys.stdout.write(str(err)+"\n")
    except:
        sys.stdout.write("\n\tunexpected error executing command\n")

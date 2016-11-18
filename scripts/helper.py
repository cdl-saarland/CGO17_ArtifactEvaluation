#!/usr/bin/env python
#
# Written for the CGO'17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
import subprocess as sp

intro = """Written for the CGO'17 artifact evaluation of the "Optimistic Loop
Optimization" paper. Please use with caution."""

def is_python_2():
    return sys.version_info[0] == 2

def get_input(msg):
    return raw_input(msg) if is_python_2() else input(msg)

def error(msg):
    sys.stderr.write("Error: " + msg + os.linesep)


def format_and_print(msg, newline = True):
    line = ""
    msg = msg.replace(os.linesep, " ")
    while "  " in msg:
        msg = msg.replace("  ", " ")
    if len(msg) <= 80:
        print(msg.center(80))
        msg = ""
    for word in msg.split(" "):
        if not word:
            continue
        if len(line) + len(word) >= 80:
            print(line)
            line = word
        elif line:
            line = line + " " + word
        else:
            line = word

    if line:
        print(line)
    if newline:
        print("")


def print_intro(function):
    print("*" * 80)
    format_and_print(function, False)
    print("*" * 80 + os.linesep)
    read_config()


def query_user_str(msg, default=None):
    if msg:
        print(os.linesep + msg)
    ans = get_input(">> " if not default else "[%s] >> " % (str(default)))
    return ans if ans or not default else default

def query_user_path(msg, default=None):
    print(os.linesep + msg)
    ans = get_input(">> " if not default else "[%s] >> " % (str(default)))
    return os.path.abspath(os.path.expanduser(ans)) if ans else default

def query_user_int(msg, default=None):
    ans = query_user_str(msg, str(default) if default else None)
    try:
        return int(ans)
    except ValueError:
        return query_user_int("")

def query_user_bool(msg, default=None):
    ans = query_user_str(msg, "y/n" if default is None else ("Y/n" if default
                                                             else "y/N"))
    if ans.lower() in ["yes", "y"]:
        return True
    elif ans.lower() in ["no", "n"]:
        return False
    elif default is not None and ans in ["Y/n", "y/N"]:
        return bool(default)
    return query_user_bool("", default)

def query_continue_or_abort():
    query_user_str("Press <Enter> to continue or <Ctr-C> to abort.")

def create_folder(path):
    if os.path.isdir(path):
        return
    try:
        os.makedirs(path)
    except Exception as e:
        print(e)
    if not os.path.isdir(path):
        error("Could not create folder '%s'! Exit!" % (path))
        sys.exit(1)

def run(cmd, abort_on_error = True):
    print(os.linesep + "Run: '%s'" % (cmd))
    try:
        return str(sp.check_output(cmd, shell=True).decode("utf-8")).strip()
    except:
        if abort_on_error:
            error("Command '%s' failed! Exit!" % (cmd))
            sys.exit(1)
        else:
            error("Command '%s' failed!" % (cmd))
        return None

def run_int(cmd, default, abort_on_error = True):
    try:
        return int(run(cmd, abort_on_error))
    except ValueError:
        return default

def get_value(name, var_types, query_fn):
    if name in globals() and type(globals()[name]) in var_types:
        return globals()[name]
    if name in os.environ:
        return var_types[0](os.environ[name])
    value = query_fn()
    if type(value) not in var_types:
        error("Type of '%s' should be '%s' but is '%s' (%s)" % (name, str(var_types), str(type(value)), str(value)))
    write_config(name, value)
    return value

def verify_value(name, var_types, script):
    if name in globals() and type(globals()[name]) in var_types:
        return globals()[name]
    if name in os.environ:
        return var_types[0](os.environ[name])
    error("%s was not set, run %s.py and check the config.py or set it as an environment variable!" % (name, script))
    sys.exit(1)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.py")
def write_config(name, var):
    old_lines = []
    if os.path.isfile(CONFIG_PATH):
        fd = open(CONFIG_PATH, "r")
        old_lines = fd.readlines()
        fd.close()

    new_lines = []
    for line in old_lines:
        if not line.startswith(name):
            new_lines.append(line)

    if type(var) == int:
        new_lines.append("%s = %i%s" % (name, var, os.linesep))
    elif type(var) == bool:
        new_lines.append("%s = %s%s" % (name, str(var), os.linesep))
    elif var is None:
        new_lines.append("%s = None%s" % (name, os.linesep))
    else:
        new_lines.append("%s = '%s'%s" % (name, str(var), os.linesep))

    new_lines.sort()
    fd = open(CONFIG_PATH, "w")
    fd.writelines(new_lines)
    fd.close()


def read_config():
    try:
        if os.path.isfile(CONFIG_PATH):
            print("Read %s" % (CONFIG_PATH))
            no = 0
            with open(CONFIG_PATH, "r") as fd:
                for line in fd.readlines():
                    if line.count("=") == 1:
                        name, value = line.split("=")
                        globals()[name.strip()] = eval(value.strip())
                        no += 1
            print("Successfully initialized %i values!%s" % (no, os.linesep))
    except Exception as e:
        error("Could not read/evaluate %s" % CONFIG_PATH)

#### Always executed!
format_and_print(intro)


#!/usr/bin/env python
#
# Written for the CGO'17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
from helper import *

function = "The %s script will download and setup an lnt test environment." % (os.path.split(__file__)[1])
print_intro(function)

def query_virtuelenv():
    default = run("which virtualenv2", False)
    if not default:
        default = run("which virtualenv", False)
    return query_user_path("[Existing] Path to virtualenv (python 2.X version!):", default)
VIRTUALENV = get_value("VIRTUALENV", [str], query_virtuelenv)

if not os.path.isfile(VIRTUALENV) and not os.path.islink(VIRTUALENV):
    error("virtuelenv is required, please check: http://llvm.org/docs/lnt/quickstart.html")
    sys.exit(1)


def query_sandbox():
    default = os.path.abspath(os.path.join(os.curdir, "sandbox"))
    return query_user_path("[New] Path to the virtual environment (sandbox) in which tests should be executed in:", default)
SANDBOX = get_value("SANDBOX", [str], query_sandbox)
create_folder(SANDBOX)

if not os.path.isdir(SANDBOX):
    error("Sandbox folder %s does not exist" % (SANDBOX))
    sys.exit(1)

run("%s %s" % (VIRTUALENV, SANDBOX), False)
if not os.path.isfile(os.path.join(SANDBOX, "bin", "python")):
    error("Sandbox creation failed!")
    sys.exit(1)
else:
    print("Sandbox created!" + os.linesep)


def query_lnt():
    default = os.path.abspath(os.path.join(os.curdir, "lnt"))
    return query_user_path("[New] Path to store lnt sources:", default)
LNT_SRC = get_value("LNT_SRC", [str], query_lnt)

if os.path.isdir(LNT_SRC):
    print("Skip cloning LNT, source folder exists")
else:
    print("Clone LNT:")
    run("git clone http://llvm.org/git/lnt %s" % (LNT_SRC))

print(os.linesep + "Set up lnt in the sandbox:")
run("%s %s install" % (os.path.join(SANDBOX, "bin", "python"),
                       os.path.join(LNT_SRC, "setup.py")))

ACTIVATE_FILE = os.path.join(SANDBOX, "bin", "activate")
if not os.path.isfile(ACTIVATE_FILE):
    error("Could not find %s, setup of lnt failed!" % (ACTIVATE_FILE))
    sys.exit(1)

print(os.linesep + sys.argv[0] + " is done!" + os.linesep)

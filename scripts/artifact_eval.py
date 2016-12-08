#!/usr/bin/env python
#
# Written for the CGO'17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
from helper import *

function = "The %s script will execute all other scripts automatically." % (sys.argv[0])
print_intro(function)

print("\n\nNOTE: SPEC2000 and SPEC2006 are proprietary benchmarks that we cannot distribute.")
USE_SPEC = query_user_bool("Do you have SPEC2000 and/or SPEC2006 locally available and want to integrate it in the evaluation?")

def query_spec():
    return os.path.abspath(os.path.join(os.curdir, "SPEC"))

if USE_SPEC:
    SPEC_SRC = get_value("SPEC_SRC", [str], query_spec)
    create_folder(SPEC_SRC)

def setup_SPEC(Year):
    print(os.linesep)

    SPECCPU_SRC = os.path.join(SPEC_SRC, "speccpu%s" % (Year))
    if os.path.islink(SPECCPU_SRC) or os.path.isdir(SPECCPU_SRC):
        print("Skip SPEC%s detection, %s exists" % (Year, SPECCPU_SRC))
        return SPECCPU_SRC

    while True:
        SRC = None
        for src in [os.path.join("/", "speccpu%s" % (Year)), os.path.join(os.path.expanduser("~"), "speccpu%s" % (Year)),os.path.join(os.path.abspath(os.curdir), "speccpu%s" % (Year))]:
            if os.path.islink(src) or os.path.isdir(src):
                if os.path.isdir(os.path.join(src, "benchspec")):
                    print("Auto detect: %s" % (src))
                    SRC = src
                    break
        if not SRC:
            SRC = query_user_path("[Existing] SPEC%s folder:" % (Year), "")
        if not os.path.isdir(SRC):
            if SRC:
                print("WARNING: '%s' is not a folder" % (SRC))
            SRC = None
        elif not os.path.isdir(os.path.join(SRC, "benchspec")):
            print("WARNING: Expected 'benchspec' folder in '%s'" % (SRC))
            SRC = None
        else:
            break
        if query_user_bool("Continue without SPEC%s?" % (Year), True):
            print("Rerun 'scripts/setup_benchmarks.py' after SPEC%s is available!" % (Year))
            break

    if SRC:
        run("ln -s %s %s" % (SRC, SPECCPU_SRC))
        print("SPEC%s was set up!" % (Year))
        return SPECCPU_SRC
    else:
        print("Failed to set up SPEC%s!" % (Year))
        return None

if USE_SPEC:
    HOSTNAME = run("hostname", False)
    HOSTNAME = HOSTNAME if HOSTNAME else "<container>"

    print(os.linesep * 2)
    print("-"*40 + "\nNote: This is only for people using the docker container:\n")
    format_and_print("""Use `docker cp <src_path> %s:/` to copy
                     files/folder (e.g., SPEC) from the host system to the root
                     directory of a docker container.""" % HOSTNAME)
    print("-"*40 + "\n")

    SPEC_2000_SRC = setup_SPEC("2000")
    SPEC_2006_SRC = setup_SPEC("2006")


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
if query_user_bool("Do you want to use the defaults (build paths, build options, etc.) for all values [recommended] or step interactively through the process?"):
    os.system('%s/artifact_eval_helper.py < %s/use_defaults' % (SCRIPT_PATH, SCRIPT_PATH))
else:
    os.system('%s/artifact_eval_helper.py' % (SCRIPT_PATH, SCRIPT_PATH))

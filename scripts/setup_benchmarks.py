#!/usr/bin/env python
#
# Written for the CGO'17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
from helper import *

function = "The %s script will download and organize all benchmarks" % (os.path.split(__file__)[1])
print_intro(function)

def query_test_suite():
    default = os.path.abspath(os.path.join(os.curdir, "test_suite"))
    return query_user_path("[New] Path to LLVM test suite:", default)
TEST_SUITE = get_value("TEST_SUITE", [str], query_test_suite)
print(os.linesep)

if os.path.isdir(TEST_SUITE):
    print("Skip cloning LLVM test suite, source folder exists")
else:
    print("Clone LLVM test suite:")
    run("git clone http://llvm.org/git/test-suite %s" % (TEST_SUITE))

if not os.path.isdir(TEST_SUITE):
    error("Test suite folder %s does not exist" % (TEST_SUITE))
    sys.exit(1)

TEST_SUITE_VERSION = run("git -C %s rev-parse HEAD" % (TEST_SUITE))
print("Test suite version: %s" % (TEST_SUITE_VERSION))
print(os.linesep)

def query_npb():
    SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
    default = os.path.abspath(os.path.join(SCRIPT_PATH, "../resources/NPB3.3-SER-C"))
    return query_user_path("[Existing] SNU NPB test suite folder:", default)
NPB_SRC = get_value("NPB_SRC", [str], query_npb)

if not os.path.isdir(NPB_SRC):
    print("WARNING: NPB folder '%s' does not exist" % (NPB_SRC))
    NPB_SRC = None
elif not os.path.isfile(os.path.join(NPB_SRC, "Makefile")):
    print("WARNING: NPB folder '%s' does not contain a Makefile" % (NPB_SRC))
    NPB_SRC = None
elif not os.path.isdir(os.path.join(NPB_SRC, "BT")):
    print("WARNING: NPB folder '%s' does not contain BT benchmark" % (NPB_SRC))
    NPB_SRC = None
elif not os.path.isfile(os.path.join(NPB_SRC, "config", "make.def")) and not os.path.islink(os.path.join(NPB_SRC, "config", "make.def")):
    print("WARNING: NPB folder '%s' does not contain a 'config/make.def'" % (NPB_SRC))
    NPB_SRC = None
else:
    print("NPB was set up!")
    print("-" * 80)
    format_and_print("""Note: Please modify the config/make.def and the
                     config/suite.def file to use LLVM+Polly. The manual lists
                     all required options and the provided files have been
                     modified accordingly. If you choose to use the provided
                     version of the SNU NPB benchmarks there is nothing to
                     do.""", False)
    print("-" * 80)


def query_spec():
    return os.path.join(TEST_SUITE, "SPEC")
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

print(os.linesep * 2)
HOSTNMAE = run("hostname", False)
HOSTNMAE = HOSTNMAE if HOSTNMAE else "<continaer>"
format_and_print("""NOTE: Use `docker cp <src_path> %s:<dst_path>` to
                 copy files/folder (e.g., SPEC) from the host system to a
                 docker container.""" % HOSTNMAE)
print(os.linesep)

SPEC_2000_SRC = setup_SPEC("2000")
SPEC_2006_SRC = setup_SPEC("2006")

YEAR = 2000
for SPECCPU_SRC in [SPEC_2000_SRC, SPEC_2006_SRC]:
    YEAR += 6
    if not SPECCPU_SRC or not os.path.isdir(SPECCPU_SRC):
        continue
    if os.path.isfile(os.path.join(SPECCPU_SRC, "version")):
        version = run("cat %s" % (os.path.join(SPECCPU_SRC, "version")), False)
    elif os.path.isfile(os.path.join(SPECCPU_SRC, "version.txt")):
        version = run("cat %s" % (os.path.join(SPECCPU_SRC, "version.txt")), False)
    else:
        version = "<n/a>"
    print("SPEC%i version: %s" % (YEAR - 6, version.strip()))


print(os.linesep + "Summary:" + os.linesep)
print("%10s: %s" % ("LLVM-TS", TEST_SUITE))
print("%10s: %s" % ("SNU NPB", NPB_SRC if NPB_SRC else "n/a"))
print("%10s: %s" % ("SPEC_SRC", SPEC_SRC if SPEC_SRC else "n/a"))
print("%10s: %s" % ("SPEC2000", SPEC_2000_SRC if SPEC_2000_SRC else "n/a"))
print("%10s: %s" % ("SPEC2006", SPEC_2006_SRC if SPEC_2006_SRC else "n/a"))

print(os.linesep + sys.argv[0] + " is done!" + os.linesep)

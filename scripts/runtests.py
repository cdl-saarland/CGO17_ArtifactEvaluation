#!/usr/bin/env python
#
# Written for the CGO'17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
import time
from helper import *

function = "The %s script will run the lnt and NPB tests." % (os.path.split(__file__)[1])
print_intro(function)

LLVM_OBJ = verify_value("LLVM_OBJ", [str], "setup_toolchain")
CLANG_PATH = os.path.join(LLVM_OBJ, "bin", "clang")
CLANGXX_PATH = os.path.join(LLVM_OBJ, "bin", "clang++")
if not os.path.isfile(CLANG_PATH):
    error("Could not find clang, tried: '%s'" % (CLANG_PATH))
    sys.exit(1)
if not os.path.isfile(CLANGXX_PATH):
    error("Could not find clang++, tried: '%s'" % (CLANGXX_PATH))
    sys.exit(1)


print("0. Determine result folder and compiler for run:")
TIME_STR = time.strftime("%b_%d_%H-%M-%S")

def query_result_path():
    default = os.path.abspath(os.path.join(os.curdir, "results"))
    return query_user_path("[New] Path to store pre-processed tests results:", default)
RESULT_BASE = get_value("RESULT_BASE", [str], query_result_path)

RESULT_FOLDER = os.path.join(RESULT_BASE, TIME_STR)
create_folder(RESULT_FOLDER)
if not os.path.isdir(RESULT_FOLDER):
    error("Could not create result folder (%s)" % (RESULT_FOLDER))
    sys.exit(1)
print(" clang: %s" % (CLANG_PATH))
print(" clang++: %s" % (CLANGXX_PATH))
print(" Result folder: %s" % (RESULT_FOLDER))


print(os.linesep)
print("1. Determine general configuration options:")
GENERAL_OPTIONS = ["-O3", "-mllvm -polly", "-mllvm -polly-invariant-load-hoisting=true"]

if query_user_bool("Run the inliner prior to Polly?", True):
    GENERAL_OPTIONS.append("-mllvm -polly-run-inliner=true")
else:
    GENERAL_OPTIONS.append("-mllvm -polly-run-inliner=false")

if query_user_bool("Assume scalars to be optimizable?", True):
    GENERAL_OPTIONS.append("-mllvm -polly-unprofitable-scalar-accs=false")
else:
    GENERAL_OPTIONS.append("-mllvm -polly-unprofitable-scalar-accs=true")

if query_user_bool("Allow to speculate on error blocks?", False):
    GENERAL_OPTIONS.append("-mllvm -polly-allow-error-blocks=false")
else:
    GENERAL_OPTIONS.append("-mllvm -polly-allow-error-blocks=true")

STATS = query_user_bool("Output compile statistics?", True)
if STATS:
    GENERAL_OPTIONS.append("-mllvm -stats")

REMARKS = query_user_bool("Output compile remarks?", True)
if REMARKS:
    GENERAL_OPTIONS.append("-Rpass-analysis=polly")

while True:
    option = query_user_str("Add user compile time option:")
    if not option:
        break
    option = option.strip()
    while "  " in option:
        option = option.replace("  ", " ")
    if option.startswith("-polly"):
        option = "-mllvm " + option
    GENERAL_OPTIONS.append(option)


print(os.linesep)
print("Tests will be run with the following options:")
for option in GENERAL_OPTIONS:
    print("\t%s" % option)

print("==> Write configuration to %s/config" % (RESULT_FOLDER))
fd = open("%s/config" % (RESULT_FOLDER), "a")
for option in GENERAL_OPTIONS:
    fd.write("%s%s" % (option, os.linesep))
fd.close()

def extract_stats(path, name):
    if not STATS:
        return

    print(os.linesep * 2)
    print("Extract Polly statistics from %s" % (path))
    output = os.path.join(RESULT_FOLDER, name + ".polly_stats")
    if os.path.isfile(path):
        recursive = False
    elif os.path.isdir(path):
        recursive = True
    else:
        error("Path '%s' does not exist!" % (path))
        return

    term = " polly-scops | polly-codegen "
    run("grep %s --no-filename -E \"%s\" %s > %s" % ("-r" if recursive else "", term, path, output))
    print("Output written to %s" % (output))

    print(os.linesep * 2)
    summary = output + ".summary"

    from summarize_stats import summarize
    summarize(output, summary)


def compile_npb():
    NPB_SRC = verify_value("NPB_SRC", [str], "setup_benchmarks")
    NPB_CONFIG = os.path.join(NPB_SRC, "config", "make.def")
    if not os.path.isfile(NPB_CONFIG) and not os.path.islink(NPB_CONFIG):
        error("Could not find NPV config, tried: %s" % NPB_CONFIG)
        sys.exit(1)

    OUT_FILE = os.path.join(RESULT_FOLDER, "NPB_compile_out")
    ERR_FILE = os.path.join(RESULT_FOLDER, "NPB_compile_err")
    print("         NPB_SRC: %s" % (NPB_SRC))
    print(" std output file: %s" % (OUT_FILE))
    print("  std error file: %s" % (ERR_FILE))
    print(os.linesep * 2)

    print("Clean the NPB source folder")
    run("cd %s && make veryclean" % (NPB_SRC))

    print(os.linesep * 2)
    print("Modify the NPB configuration for this run")
    with open(NPB_CONFIG, "r") as fd:
        lines = fd.readlines()

    with open(NPB_CONFIG, "w") as fd:
        for line in lines:
            line = line.strip()
            if line.startswith("CC"):
                fd.write("CC = %s%s" % (CLANG_PATH, os.linesep))
                print(" Set CC=%s" % (CLANG_PATH))
            elif line.startswith("UCC"):
                fd.write("UCC = $(CC)%s" % (os.linesep))
            elif "CFLAGS" in line and "+=" in line:
                print("   Drop: '%s'" % (line))
                continue
            else:
                fd.write(line + os.linesep)

        for option in GENERAL_OPTIONS:
            line = "CFLAGS += %s" % (option)
            print(" Append: '%s'" % (line))
            fd.write(line + os.linesep)

    print(os.linesep * 2)
    print("Compile the NPB test suite")
    run("cd %s && make suite > %s 2> %s" % (NPB_SRC, OUT_FILE, ERR_FILE))

    extract_stats(ERR_FILE, "NPB")

    RESULT_NPB_BIN = os.path.join(RESULT_FOLDER, "NPB_bin")
    print(os.linesep * 2)
    print("Copy benchmark binaries to %s" % (RESULT_NPB_BIN))
    run("cp -R %s %s" % (os.path.join(NPB_SRC, "bin"), RESULT_NPB_BIN))

    print(os.linesep * 2)
    format_and_print("====== DONE COMPILING NPB ======")
    print(os.linesep * 2)

def get_activate_file():
    SANDBOX = verify_value("SANDBOX", [str], "setup_lnt")
    return os.path.join(SANDBOX, "bin", "activate")

def get_lnt_runtest_cmd(options):
    SANDBOX = verify_value("SANDBOX", [str], "setup_lnt")
    TEST_SUITE = verify_value("TEST_SUITE", [str], "setup_benchmarks")
    JOBS = verify_value("JOBS", [int], "setup_toolchain")
    lnt_runtest = "lnt runtest nt --sandbox %s --cc %s --cxx %s --test-suite %s --build-threads %i" % (SANDBOX, CLANG_PATH, CLANGXX_PATH, TEST_SUITE, JOBS)
    for option in options:
        lnt_runtest += " " + option
    for option in GENERAL_OPTIONS:
        lnt_option = option.replace(" ", " --cflag=")
        lnt_option = lnt_option.strip()
        if not lnt_option.startswith("--cflag"):
            lnt_option = "--cflag=" + lnt_option
        lnt_runtest += " " + lnt_option
    print("LNT runtest command:%s%s" % (os.linesep, lnt_runtest))
    return lnt_runtest

def compile_and_run_lnt(name, options):
    ACTIVATE_FILE = get_activate_file()
    lnt_setup = "source %s" % (ACTIVATE_FILE)
    lnt_deactivate = "deactivate"

    SAMPLES = query_user_int("Accumulate test data from multiple runs?", 1)
    options.append("--multisample=%i" % (SAMPLES))

    if query_user_bool("Remove short running regression tests?", False):
        options.append("--benchmarking-only")

    options.append("--run-order=%s_%s" % (TIME_STR, name))
    def query_lnt_server():
        default = os.path.join(RESULT_BASE, "lnt_server")
        return query_user_path("[New] LNT server to commit results to (if any):", default)
    global LNT_SERVER
    LNT_SERVER = get_value("LNT_SERVER", [str, type(None)], query_lnt_server)

    if LNT_SERVER:
        if not os.path.isdir(LNT_SERVER):
            print("Create lnt server instance %s" % (LNT_SERVER))
            run("%s && lnt create %s" % (lnt_setup, LNT_SERVER), False)
        if os.path.isdir(LNT_SERVER):
            options.append("--submit=%s" % (LNT_SERVER))

    lnt_runtest = get_lnt_runtest_cmd(options)

    sandbox_ls_before = os.listdir(os.path.abspath(SANDBOX))

    print("Run LNT:")
    run("%s && %s; %s" % (lnt_setup, lnt_runtest, lnt_deactivate))

    sandbox_ls_after = os.listdir(os.path.abspath(SANDBOX))
    for item in sandbox_ls_before:
        if item in sandbox_ls_after:
            sandbox_ls_after.remove(item)
        else:
            error("File/Folder %s disappeared..." % item)

    if len(sandbox_ls_after) != 1:
        error("Could not determine the folder lnt executed in. Automatic summary skipped!")
        return

    folder = os.path.abspath(os.path.join(SANDBOX, sandbox_ls_after[0]))
    print("LNT execution folder was: %s" % (folder))

    RESULT_LNT_FOLDER = os.path.join(RESULT_FOLDER, name)
    print("Move lnt execution folder to %s" % (RESULT_LNT_FOLDER))
    run("mv %s %s" % (folder, RESULT_LNT_FOLDER))

    extract_stats(RESULT_LNT_FOLDER, name)

    print(os.linesep * 2)
    format_and_print("====== DONE COMPILING & RUNNING LNT ======")
    print(os.linesep * 2)

def compile_and_run_test_suite():
    compile_and_run_lnt("test_suite", [])

def compile_and_run_spec():
    SPEC_SRC = verify_value("SPEC_SRC", [str], "setup_benchmarks")
    compile_and_run_lnt("spec", ["--test-externals=%s" % (SPEC_SRC), "--only-test=External"])


if query_user_bool("Compile the NPB suite?", True):
    compile_npb()

if query_user_bool("Compile & run the LLVM test suite?", True):
    compile_and_run_test_suite()

if query_user_bool("Compile & run the SPEC test suite(s)?", True):
    compile_and_run_spec()

LNT_SERVER = get_value("LNT_SERVER", [str, type(None)], lambda: "")
if LNT_SERVER and os.path.isdir(LNT_SERVER):
    if query_user_bool("Run lnt server instance %s" % (LNT_SERVER)):
        run("lnt runserver %s" % (LNT_SERVER))

print(os.linesep + sys.argv[0] + " is done!" + os.linesep)

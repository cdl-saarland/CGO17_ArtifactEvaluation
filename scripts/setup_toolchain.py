#!/usr/bin/env python
#
# Written for the CGO'17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
from helper import *

function = "The %s script will download and build LLVM, Clang and Polly." % (os.path.split(__file__)[1])
print_intro(function)

print(os.linesep + "1. Determine the system parameters:")

def query_jobs():
    default = run_int("cat /proc/cpuinfo | grep processor | wc -l", 1, False)
    return query_user_int("How many jobs should be used?", default)
JOBS = get_value("JOBS", [int], query_jobs)

def query_memory():
    default = run_int("free -g | grep 'Mem' | grep -o -E '[0-9]*$'", 2, False)
    return query_user_int("How much memory in GB is available?", default)
MEMORY = get_value("MEMORY", [int], query_memory)


def query_compiler(lang):
    return lambda : query_user_path("[Existing] Path to the %s11 compatible compiler [use system compiler]" % (lang))
CC = get_value("CC", [str, type(None)], query_compiler("C"))
CXX= get_value("CXX", [str, type(None)], query_compiler("C++"))

def query_toolchain():
    default = os.path.abspath(os.path.join(os.curdir, 'toolchain'))
    return query_user_path("[New] Toolchain base folder:", default)
TOOLCHAIN_BASE = get_value("TOOLCHAIN_BASE", [str], query_toolchain)
create_folder(TOOLCHAIN_BASE)

print(os.linesep + "System parameters determined! Summary:" + os.linesep)
print("%15s: %i" % ("Jobs", JOBS))
print("%15s: %iGB" % ("Memory", MEMORY))
print("%15s: %s" % ("CC", CC if CC else "system default"))
print("%15s: %s" % ("CXX", CXX if CXX else "system default"))
print("%15s: %s" % ("Base path", TOOLCHAIN_BASE))

query_continue_or_abort()

LLVM_SRC = os.path.join(TOOLCHAIN_BASE, "llvm_src")
CLANG_SRC = os.path.join(TOOLCHAIN_BASE, "llvm_src", "tools", "clang")
POLLY_SRC = os.path.join(TOOLCHAIN_BASE, "llvm_src", "tools", "polly")
write_config("LLVM_SRC", LLVM_SRC)
write_config("CLANG_SRC", CLANG_SRC)
write_config("POLLY_SRC", POLLY_SRC)

print(os.linesep + "Download LLVM, Clang and Polly:")

print("%s%10s: %s" % (os.linesep, "LLVM src", LLVM_SRC))
if os.path.isdir(LLVM_SRC):
    print("Skip cloning LLVM, source folder exists")
else:
    print("Clone LLVM:")
    run("git clone http://llvm.org/git/llvm.git %s" % (LLVM_SRC))

print("%s%10s: %s" % (os.linesep, "Clang src", CLANG_SRC))
if os.path.isdir(CLANG_SRC):
    print("Skip cloning Clang, source folder exists")
else:
    print("Clone Clang:")
    run("git clone http://llvm.org/git/clang.git %s" % (CLANG_SRC))

print("%s%10s: %s" % (os.linesep, "Polly src", POLLY_SRC))
if os.path.isdir(POLLY_SRC):
    print("Skip cloning Polly, source folder exists")
else:
    print("Clone Polly:")
    run("git clone http://llvm.org/git/polly.git %s" % (POLLY_SRC))


print(os.linesep)
if query_user_bool("Revert to original artifact evaluation version?", False):
    LLVM_AE_VERSION = "b28b8f21ef30c677f418ad6cc1acd4792552f672"
    CLANG_AE_VERSION = "9483fa6dbe01ac2b7513a2bf50dcb599ebe4af46"
    POLLY_AE_VERSION = "5df868addaca89cae91e1328af6682b56d06b572"

    print("Reset LLVM to %s:" % (LLVM_AE_VERSION))
    run("git -C %s reset --hard %s" % (LLVM_SRC, LLVM_AE_VERSION))

    print("Reset Clang to %s:" % (CLANG_AE_VERSION))
    run("git -C %s reset --hard %s" % (CLANG_SRC, CLANG_AE_VERSION))

    print("Reset Polly to %s:" % (POLLY_AE_VERSION))
    run("git -C %s reset --hard %s" % (POLLY_SRC, POLLY_AE_VERSION))

try:
    LLVM_VERSION = run("git -C %s rev-parse HEAD" % (LLVM_SRC))
    print("LLVM version: %s" % (LLVM_VERSION))
    CLANG_VERSION = run("git -C %s rev-parse HEAD" % (CLANG_SRC))
    print("Clang version: %s" % (CLANG_VERSION))
    POLLY_VERSION = run("git -C %s rev-parse HEAD" % (POLLY_SRC))
    print("Polly version: %s" % (POLLY_VERSION))
except:
    error("""Could not determine versions of LLVM/Clang/Polly! Maybe the download
          was interrupted or the source folders are otherwise corrupt. Please
          delete them and restart the process.""")

def determine_obj_path():
    return os.path.join(TOOLCHAIN_BASE, "llvm_obj")
LLVM_OBJ = get_value("LLVM_OBJ", [str], determine_obj_path)
create_folder(LLVM_OBJ)

if not os.path.isdir(LLVM_OBJ):
    error("Could not create llvm build dir '%s'" % (LLVM_OBJ))
    sys.exit(1)

print("%sConfigure LLVM in %s%s" % (os.linesep, LLVM_OBJ, os.linesep))

CMAKE_OPTIONS = ['-DLINK_POLLY_INTO_TOOLS=1', '-DBUILD_SHARED_LIBS=1']

def query_debug():
    return query_user_bool("Use Debug build?", False)
DEBUG = get_value("DEBUG", [bool], query_debug)

if DEBUG:
    CMAKE_OPTIONS.append("-DCMAKE_BUILD_TYPE=Debug")
else:
    CMAKE_OPTIONS.append("-DCMAKE_BUILD_TYPE=Release")

def query_assertions():
    return query_user_bool("Enable assertions in build?", True)
ASSERTIONS = get_value("ASSERTIONS", [bool], query_assertions)

CMAKE_OPTIONS.append("-DLLVM_ENABLE_ASSERTIONS=%s" % (str(ASSERTIONS)))

def query_ninja():
    found = run("which ninja", False)
    return found and query_user_bool("Use ninja instead of make?", False)
NINJA = get_value("NINJA", [bool], query_ninja)

if NINJA:
    if DEBUG:
        CMAKE_OPTIONS.append("-DLLVM_PARALLEL_LINK_JOBS=%i" % (max(1, MEMORY / 4)))
    else:
        CMAKE_OPTIONS.append("-DLLVM_PARALLEL_LINK_JOBS=%i" % (max(1, MEMORY / 2)))
    CMAKE_OPTIONS.append("-DLLVM_PARALLEL_COMPILE_JOBS=%i" % (max(1, JOBS)))
    CMAKE_OPTIONS.append("-G")
    CMAKE_OPTIONS.append("Ninja")

run("cd %s && cmake %s %s" % (LLVM_OBJ, LLVM_SRC, " ".join(CMAKE_OPTIONS)))


print(os.linesep + "Build LLVM (this might take some time)")
if NINJA:
    run("ninja -C %s" % (LLVM_OBJ))
    run("ninja -C %s check-polly" % (LLVM_OBJ))
else:
    run("make -C %s -j %i" % (LLVM_OBJ, max(1, MEMORY / (4 if DEBUG else 2), JOBS)))
    run("make -C %s check-polly" % (LLVM_OBJ))

print(os.linesep + sys.argv[0] + " is done!" + os.linesep)

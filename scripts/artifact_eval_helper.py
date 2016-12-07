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

print(os.linesep)
print_intro("1. Set up the toolchain!")
from setup_toolchain import *

print(os.linesep)
print_intro("2. Set up the benchmarks!")
from setup_benchmarks import *

print(os.linesep)
print_intro("3. Set up the test environment (lnt)!")
from setup_lnt import *

print(os.linesep)
print_intro("4. Run the tests!")
from runtests import *

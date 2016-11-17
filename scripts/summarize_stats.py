#!/usr/bin/env python
#
# Written for the CGO"17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
import time
from helper import *

function = "The %s script will parse and summarize LLVM statistics." % (os.path.split(__file__)[1])

def summarize(inp, out):
    print("Summarize statistics in %s" % inp)
    stats = {}
    with open(inp, "r") as fd:
        for line in fd:
            try:
                line = line.strip()
                idx = line.index(" ")
                num = int(line[:idx])
                line = line[idx:].strip()
                key = line[line.index(" "):].strip()
                if key in stats:
                    stats[key] += num
                else:
                    stats[key] = num
            except:
                error("Unknown error while parsing: '%s'" % (line))

    with open(out, "w") as fd:
        keys = list(stats.keys())
        keys.sort()
        for key in keys:
            fd.write("%10i %s%s" % (stats[key], key, os.linesep))
    print("Summary written to %s" % out)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        print_intro(function)
        summarize(sys.argv[1], sys.argv[2])
        print(os.linesep + sys.argv[0] + " is done!" + os.linesep)
    else:
        error("Usage: %s <input_file> <output_file>" % ((os.path.split(__file__)[1])))


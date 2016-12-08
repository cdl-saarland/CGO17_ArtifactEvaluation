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

RESULT_BASE = get_value("RESULT_BASE", [str], lambda: "")
summaries = []
if os.path.isfile("%s/summaries" % RESULT_BASE):
    with open("%s/summaries" % RESULT_BASE, "r") as fd:
        for line in fd.readlines():
            summaries.append(line.split("|")[:2])

for name,summary in summaries:
    if query_user_bool("\n\nDo you want to print out the summary for %s?" % (name), False):
        os.system("cat %s" % summary)

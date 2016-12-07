#!/usr/bin/env python
#
# Written for the CGO"17 artifact evaluation of the "Optimistic Loop
# Optimization" paper.
#
# Please use with caution.

import os
import sys
import time
import subprocess as sb
from helper import *

function = "The %s script will parse and summarize LLVM statistics." % (os.path.split(__file__)[1])

def summarize(inp, out, rtc_folders=[], minimal=False):
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
                key = key[2:]
                if key in stats:
                    stats[key] += num
                else:
                    stats[key] = num
            except:
                error("Unknown error while parsing: '%s'" % (line))

    values = {}
    for name,rtc_folder in rtc_folders:
        try:
            values['Number of failing RTCs'] = int(run("grep -R --no-filename 'RTC: 0' %s | wc -l " % rtc_folder, False, -1))
        except Exception as e:
            print(e)
            pass
        try:
            values['Number of failing RTC locations'] = int(run("grep -R --no-filename 'RTC: 0' %s | sed -e 's|.*\\(F: [-_.a-zA-Z0-9]* R:\\)|\\1|' -e 's|__RTC:.*||' | grep -v 'Binary file' | sort -u | wc -l" % rtc_folder, False, -1))
        except Exception as e:
            print(e)
            pass
        try:
            values['Number of executed RTCs'] = int(run("grep -R --no-filename 'RTC: ' %s | wc -l " % rtc_folder, False, -1))
        except Exception as e:
            print(e)
            pass
        try:
            values['Number of executed RTC locations'] = int(run("grep -R --no-filename 'RTC: ' %s | sed -e 's|.*\\(F: [-_.a-zA-Z0-9]* R:\\)|\\1|' -e 's|__RTC:.*||' | grep -v 'Binary file' | sort -u | wc -l" % rtc_folder, False, -1))
        except Exception as e:
            print(e)
            pass

    lines = []

    lines.append("\n\nStatistic data summarized [-mllvm -stats]:\n")
    lines.append("-----------------------------------------\n")
    keys = list(stats.keys())
    keys.sort()
    for key in keys:
        lines.append("%10i - %s%s" % (stats[key], key, os.linesep))
        values[key] = stats[key]

    lines.append("\n\nComputed experimental result data:\n")
    lines.append("---------------------------------\n")

    lines.append("Number of valid non-trivial loop nests [#S (a)]:\n")
    valid_scops = values.get("Number of valid Scops", 0)
    complex_scops = values.get("Number of too complex SCoPs.", 0)
    unprofitable_scops = values.get("Number of unprofitable SCoPs.", 0)
    valid_profitable_scops = valid_scops - complex_scops - unprofitable_scops
    lines.append(" %5i : Valid SCoPs\n" % (valid_scops))
    lines.append("-%5i : Too complex SCoPs\n" % (complex_scops))
    lines.append("-%5i : Unprofitable SCoPs\n" % (unprofitable_scops))
    lines.append("-------\n")
    lines.append("=%5i : Valid profitable SCoPs [#S (a)]\n\n\n" % (valid_profitable_scops))

    lines.append("Number of valid non-trivial loop nests with infeasible assumptions [#S (b)]:\n")
    infeasible_scops = values.get("Number of SCoPs with statically infeasible context.", 0)
    valid_infeasible_scops = infeasible_scops - complex_scops - unprofitable_scops
    lines.append(" %5i : Infeasible SCoPs\n" % (infeasible_scops))
    lines.append("-%5i : Too complex SCoPs\n" % (complex_scops))
    lines.append("-%5i : Unprofitable SCoPs\n" % (unprofitable_scops))
    lines.append("-------\n")
    lines.append("=%5i : Valid infeasible SCoPs [#S (b)]\n\n\n" % (valid_infeasible_scops))

    lines.append("Number of valid non-trivial loop nests without assumptions [#S (w/o A)]:\n")
    versioned_scops = values.get("Number of SCoPs that required versioning.", 0)
    valid_scops_no_assumptions = valid_profitable_scops - versioned_scops
    lines.append(" %5i : Valid profitable SCoPs [#S (a)]\n" % (valid_profitable_scops))
    lines.append("-%5i : SCoPs that required versioning\n" % (versioned_scops))
    lines.append("-------\n")
    lines.append("=%5i : Valid profitable SCoPs without assumptions [#S (w/o A)]\n\n\n" % (valid_scops_no_assumptions))

    lines.append("Number of inbounds/delinearization assumptions taken [IB]:\n")
    inbounds_assumptions = values.get("Number of inbounds assumptions taken.", 0)
    delin_assumptions = values.get("Number of delinearization assumptions taken.", 0)
    lines.append(" %5i : Number of delinearization assumptions taken\n" % (delin_assumptions))
    lines.append("+%5i : Number of inbounds assumptions taken\n" % (inbounds_assumptions))
    lines.append("-------\n")
    lines.append("=%5i : inbounds assumptions [IB]\n\n\n" % (inbounds_assumptions + delin_assumptions))

    lines.append("Number of expression evaluation (wrapping) assumptions taken [EE]:\n")
    wrapping_assumption = values.get("Number of wrapping assumptions taken.", 0)
    lines.append("=%5i : expression evaluation assumptions [EE]\n\n\n" % (wrapping_assumption))

    lines.append("Number of bounded loop assumptions taken [BL]:\n")
    bounded_loops_assumption = values.get("Number of bounded loop assumptions taken.", 0)
    lines.append("=%5i : bounded loop assumptions [BL]\n\n\n" % (bounded_loops_assumption))

    lines.append("Number of alias assumptions taken [AA]:\n")
    alias_assumption = values.get("Number of aliasing assumptions taken.", 0)
    lines.append("=%5i : alias assumptions [AA]\n\n\n" % (alias_assumption))

    lines.append("Number of referential transparent (invariant load) assumptions taken [RT]:\n")
    inv_load_assumption = values.get("Number of invariant loads assumptions taken.", 0)
    lines.append("=%5i : referential transparent assumptions [RT]\n\n\n" % (inv_load_assumption))

    d_a = d_b = e_a = e_b = d_na = e_na = "n/a"
    if 'Number of executed RTC locations' in values.keys():
        d_a = values.get('Number of executed RTC locations', 0)
        lines.append('Number of executed RTC locations [#D (a)]: %7i\n\n' % d_a)
    if 'Number of failing RTC locations' in values.keys():
        d_b = values.get('Number of failing RTC locations', 0)
        lines.append('Number of failing RTC locations [#D (b)]: %7i\n\n' % d_b)
    if 'Number of executed RTCs' in values.keys():
        e_a = values.get('Number of executed RTCs', 0)
        lines.append('Number of executed RTCs [#E (a)]: %7i\n\n' % e_a)
    if 'Number of failing RTCs' in values.keys():
        e_b = values.get('Number of failing RTCs', 0)
        lines.append('Number of failing RTCs [#E (b)]: %7i\n\n' % e_b)

    s_a = valid_profitable_scops
    s_b = valid_infeasible_scops
    s_na = valid_scops_no_assumptions
    ib_a = inbounds_assumptions + delin_assumptions
    ee_a = wrapping_assumption
    bl_a = bounded_loops_assumption
    aa_a = alias_assumption
    rt_a = inv_load_assumption
    ib_b = ee_b = bl_b = aa_b = rt_b = "n/a"
    if minimal:
        ib_a,ib_b = ib_b,ib_a
        ee_a,ee_b = ee_b,ee_a
        bl_a,bl_b = bl_b,bl_a
        aa_a,aa_b = aa_b,aa_a
        rt_a,rt_b = rt_b,rt_a

    contains_rtc_values = d_a != 'n/a' or d_b != 'n/a' or e_a != 'n/a' or e_b != 'n/a'

    with open(out, "w") as fd:
        fd.write("Summary of the statistics in %s\n\n" % (inp))
        fd.write("\tSummary %s runtime execution information [-mllm -polly-codegen-emit-rtc-print]\n" % ('contains' if contains_rtc_values else 'does not contain'))
        fd.write("\t%s assumptions were tracked [-mllm -polly-remarks-minimal]\n\n" % ('Only non-implied' if minimal else 'All'))

        fd.write('Applicability & runtime results (if available):\n')
        fd.write('----------------------------------------------\n')
        fd.write('   %10s   w/ A  %10s |  w/o A  \n' % ('(a)','(b)'))
        fd.write('   %10s---------%10s-|---------\n' % ('-'*10,'-'*10))
        fd.write('#S %10s    |    %10s |  %5s    \n' % (str(s_a),str(s_b),str(s_na)))
        fd.write('#D %10s    |    %10s |  %5s    \n' % (str(d_a),str(d_b),str(d_na)))
        fd.write('#E %10s    |    %10s |  %5s    \n' % (str(e_a),str(e_b),str(e_na)))

        fd.write('\nAssumptions taken:\n')
        fd.write('-----------------\n')
        fd.write('      %10s   w/ A  %10s \n' % ('(a)','(b)'))
        fd.write('A[%s] %10s    |    %10s \n' % ('IB',str(ib_a),str(ib_b)))
        fd.write('A[%s] %10s    |    %10s \n' % ('EE',str(ee_a),str(ee_b)))
        fd.write('A[%s] %10s    |    %10s \n' % ('BL',str(bl_a),str(bl_b)))
        fd.write('A[%s] %10s    |    %10s \n' % ('AA',str(aa_a),str(aa_b)))
        fd.write('A[%s] %10s    |    %10s \n' % ('RT',str(rt_a),str(rt_b)))

        fd.write('\n\nRaw data and processing step follow!\n')

        for line in lines:
            fd.write(line)

    print("Summary written to %s" % out)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        print_intro(function)
        rtc_folders = []
        i = 3
        while i + 1 < len(sys.argv):
            rtc_folders.append((sys.argv[i], sys.argv[i+1]))
            i+=2
        minimal = len(sys.argv) == i + 1 and sys.argv[i] == 'minimal'
        summarize(sys.argv[1], sys.argv[2], rtc_folders, minimal)
        print(os.linesep + sys.argv[0] + " is done!" + os.linesep)
    else:
        error("Usage: %s <input_file> <output_file>" % ((os.path.split(__file__)[1])))


#!/usr/bin/env python
import subprocess
import socket
import time
import sys
import glob


gcoverage = [0, 0, 0, 0]


DIR=sys.argv[1]

print "%-16s %4s %4s %3s %6s %5s %3s     %s" % ('Name', 'Branches', 'Taken', '', 'Lines', 'Exec', '', 'Missing')
print "----------------------------------------------------------------"
for filename in sorted(glob.glob(DIR + "/*.c.gcov")):
    fd = open(filename, 'rb')

    branch_taken = 0
    branch_all = 0
    branch_missed = []

    lines = []
    badlines = 0
    for line in fd:
        if line.startswith('call') or line.startswith('function'):
            continue
        if line.startswith('branch'):
            branch_all += 1
            if line.split()[3].strip() in ['0', 'executed']:
                branch_missed.append(str(lineno))
            else:
                branch_taken += 1
            continue
        runs, lineno, line = line.split(":",2)
        runs = runs.strip()
        lineno = int(lineno.strip())
        if runs == "-" or lineno==0:
            continue
        if runs[0] == "#":
            badlines +=1
        lines.append( (runs, lineno) )

    rets = []
    first_run, first_lineno, last_lineno = None, None, None
    for runs, lineno in lines:
        if runs != first_run:
            if first_run:
                if first_run[0] == "#":
                    rets.append( (first_lineno, last_lineno or first_lineno) )
            first_run = runs
            first_lineno = lineno
            last_lineno = None
        else:
            last_lineno = lineno
    if first_run and first_run[0] == "#":
        rets.append( (first_lineno, last_lineno or first_lineno) )
    fd.close()
    good, all = (len(lines)-badlines), float(len(lines))
    coverage = (good / (all or 1))*100.0
    branch_cov = (branch_taken/float(branch_all or 1)) * 100
    gcoverage[0] += good
    gcoverage[1] += all
    gcoverage[2] += branch_taken
    gcoverage[3] += branch_all
    slots = []
    maxdiff = max(map(lambda (a,b):b-a, rets) or [0])
    maxdiff = max(2, maxdiff)
    for a, b in rets:
        s = "%i-%i" % (a,b) if a!=b else '%i' % a
        if b-a == maxdiff: s = "*" + s + "*"
        slots.append(s)
    print "%-20s %4i %4i %3.0f%% %6i %5i  %3.0f%%   %s " % (filename.rpartition(".")[0], 
            branch_all, branch_taken, branch_cov,
            all, good, coverage, 
            ', '.join(branch_missed) + ' | ' +
            ', '.join(slots))

print "----------------------------------------------------------------"
code_cov = (gcoverage[0]/float(gcoverage[1] or 1)) * 100
branch_cov = (gcoverage[2]/float(gcoverage[3] or 1)) * 100
print "%-20s %4i %4i %3.0f%% %6i %5i  %3.0f%%   %s " % ('TOTAL',
        gcoverage[3], gcoverage[2], branch_cov,
        gcoverage[1], gcoverage[0], code_cov, '')


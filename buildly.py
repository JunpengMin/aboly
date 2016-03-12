# coding: utf-8

from __future__ import unicode_literals, print_function
import os
import subprocess
import sys


def main():
    BUILD_CMD = r'xelatex "\newcommand{\buildnoly}{%d} \newcommand{\lycommitno}{%s} \input{ly.tex}"'
    COMMITNO_CMD = r'git rev-parse HEAD'
    BUILDNO_FILE = 'buildnoly.txt'  # shabby toy of my own; not included in the GitHub project

    if subprocess.call([sys.executable, 'autolybody.py']) != 0:
        print("Failed to run autolybody.py", file=sys.stderr)
        return 1

    buildno = 0
    use_buildno_file = os.path.isfile(BUILDNO_FILE)
    if use_buildno_file:
        try:
            with open(BUILDNO_FILE) as fin:
                buildno = int(fin.read()) + 1
        except Exception:
            use_buildno_file = False
    try:
        commitno = subprocess.check_output(COMMITNO_CMD).strip()
    except subprocess.CalledProcessError:
        commitno = 0
    r = subprocess.call(BUILD_CMD % (buildno, commitno))
    if r == 0 and use_buildno_file:
        with open(BUILDNO_FILE, 'w') as fout:
            fout.write(str(buildno))
    return r


if __name__ == '__main__':
    sys.exit(main())

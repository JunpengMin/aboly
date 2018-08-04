#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function
import logging
import os
import subprocess
import sys

import validate


def main():
    BUILD_CMD = [
        'xelatex',
        r'\newcommand\buildnoaboly{%d} \newcommand{\lycommitno}{%s} \input{aboly.tex}'
    ]
    COMMITNO_CMD = ['git', 'rev-parse', 'HEAD']
    BUILDNO_FILE = 'buildnoaboly.txt'  # shabby toy of my own; not included in the GitHub project
    LOG_FILE = 'abolylog.txt'

    logging.basicConfig(
        format='【%(asctime)s - %(levelname)s】%(message)s',
        filename=LOG_FILE,
        filemode='w',  # or 'a'
        level=logging.INFO)
    log = logging.getLogger()
    log.addHandler(logging.StreamHandler())  # log to file and stderr

    for f in ('autobody.py', 'autocharacters.py', 'autotopics.py'):
        if subprocess.call([sys.executable, f]) != 0:
            log.error('Failed to run %s', f)
            return 1

    for validator in validate.validators:
        if not validator(log):
            log.error('Failed validator %s', validator.__name__)
            return 1

    buildno = 0
    use_buildno_file = os.path.isfile(BUILDNO_FILE)
    if use_buildno_file:
        try:
            with open(BUILDNO_FILE) as fin:
                buildno = int(fin.read()) + 1
        except Exception:
            log.warning('No build number')
            use_buildno_file = False
    try:
        commitno = subprocess.check_output(COMMITNO_CMD).strip().decode(
            'ascii')
    except subprocess.CalledProcessError:
        log.warning('No commit number')
        commitno = 0
    BUILD_CMD[1] = BUILD_CMD[1] % (buildno, commitno)
    r = subprocess.call(BUILD_CMD)
    if r != 0:
        log.error('Failed to build aboly with error code %d', r)
    elif use_buildno_file:
        with open(BUILDNO_FILE, 'w') as fout:
            fout.write(str(buildno))
    logging.shutdown()
    if os.path.isfile(LOG_FILE) and os.stat(LOG_FILE).st_size != 0:
        print('Check your log file:', LOG_FILE)
    return r


if __name__ == '__main__':
    sys.exit(main())

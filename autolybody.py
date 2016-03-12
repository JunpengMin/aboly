# coding: utf-8

from __future__ import unicode_literals
import io
import re
import sys


def main():
    BODY = 'body.tex'
    BODY_OUT = 'autolybody.tex'
    ENCODING = 'utf-8'

    with io.open(BODY, encoding=ENCODING) as fin:
        body = fin.read()

    body = re.sub(r'\\lychar\{(.+?)\}', r'\1', body)
    body = re.sub(r'\\lycharlink\{.+\}\{(.+?)\}', r'\1', body)
    body = re.sub(r'\\lylink\{.+\}\{(.+?)\}', r'\1', body)
    body = '\n\n\n'.join(re.findall(r'\\(?:chapter|lyblob)a?\{(?:.+?)\}', body, re.S))
    body = body.replace(r'\lybloba', r'\lyblob')
    body = body.replace(r'\lyblob', r'\lyblobraw')

    with io.open(BODY_OUT, 'w', encoding=ENCODING) as fout:
        fout.write(body)


if __name__ == '__main__':
    sys.exit(main())

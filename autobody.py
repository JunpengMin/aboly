# coding: utf-8

from __future__ import unicode_literals
import io
import sys


# \lychar* --> \lycharlink
def auto_lychars(bodyfile, cmapfile, encoding):
    with io.open(bodyfile, encoding=encoding) as fin:
        body = fin.read()
    with io.open(cmapfile, encoding=encoding) as fin:
        cmaps = fin.read().splitlines()
    for cm in cmaps:
        chunks = cm.split(' ')
        target = chunks[-1]
        for name in chunks[:-1]:
            old = r'\lychar{%s}' % name
            repl = r'\lycharlink{%s}{%s}' % (target, name)
            body = body.replace(old, repl)

    specials = {
        r'\lychar{伯夷}': r'\lycharlink{boyishuqi}{伯夷}',
        r'\lychar{叔齐}': r'\lycharlink{boyishuqi}{叔齐}',
    }
    for old, repl in specials.items():
        body = body.replace(old, repl)
    return body


def main():
    CHARACTERS_MAP = 'characters_map.txt'
    ENCODING = 'utf-8'
    BODY = 'body.tex'
    BODY_OUT = 'autobody.tex'

    body = auto_lychars(BODY, CHARACTERS_MAP, ENCODING)

    with io.open(BODY_OUT, 'w', encoding=ENCODING) as fout:
        fout.write(body)


if __name__ == '__main__':
    sys.exit(main())

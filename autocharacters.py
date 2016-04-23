# coding: utf-8

from __future__ import unicode_literals
import io
import re
import sys


def extract_blob_title(content):
    r'''Extract text inside \lyblob{}.'''
    left = content.index('{') + 1
    right = left
    count = 1
    while count != 0:
        if content[right] == '{':
            count += 1
        elif content[right] == '}':
            count -= 1
        right += 1
    return content[left:right]


def get_label_blobs(content):
    CHAPTER_PREFIX = r'\chapter'
    BLOB_PREFIX = r'\lyblob'
    BLOB_TEMPLATE = '%d.%d'
    LABEL_PAT = re.compile(r'\lycharlink\{(.+?)\}\{.+?\}')
    chapter_count = 0
    blob_count = 0

    lines = content.splitlines(True)
    lbs = {}
    for i, line in enumerate(lines):
        if line.lstrip().startswith(CHAPTER_PREFIX):
            chapter_count += 1
            blob_count = 0
        elif line.lstrip().startswith(BLOB_PREFIX):
            blob_count += 1
            left = content.index(line)
            assert content[left+len(line):].find(line) == -1  # no duplicate \lyblob line
            title = extract_blob_title(content[left:])
            mats = LABEL_PAT.finditer(title)
            if mats:
                blob = BLOB_TEMPLATE % (chapter_count, blob_count)
                if blob == BLOB_TEMPLATE % (11, 3):  # NOTE: skip 四科十哲
                    continue
                for m in mats:
                    label = m.group(1)
                    if label not in lbs:
                        lbs[label] = [blob]
                    else:
                        if blob not in lbs[label]:
                            lbs[label].append(blob)
    return lbs


def append_annotations(content, label_blobs):
    LABEL_LINE_PREFIX = r'\lylabel{'
    CONTENT_LINE_PREFIX = r'\lycharname{'
    STOP_PREFIXES = {LABEL_LINE_PREFIX, r'\lypdfbookmark'}
    ANNOTATION_TEMPLATE = r'\lyref{%s}'
    lines = content.splitlines(True)
    line_count = len(lines)

    for i, line in enumerate(lines):
        if not line.isspace():
            line = line.lstrip()
            if line.startswith(LABEL_LINE_PREFIX):
                left = line.index(LABEL_LINE_PREFIX) + len(LABEL_LINE_PREFIX)
                label = line[left: line.index('}', left)]
                if label in ('characters', 'zisi', 'shaogong', 'boyi', 'houyi', 'lijiliyun'):  # special cases
                    continue
                if i == line_count-1 or not lines[i+1].lstrip().startswith(CONTENT_LINE_PREFIX):
                    raise RuntimeError("Line %d of characters.tex is malformatted" % (i+2))
                j = i+1
                while j != line_count-1 and all(not lines[j].startswith(sp) for sp in STOP_PREFIXES):
                    j += 1
                j -= 1
                while lines[j] == '' or lines[j].isspace() or lines[j].lstrip().startswith('%'):
                    j -= 1
                blobs = label_blobs[label]
                lines[j] += ' '.join(ANNOTATION_TEMPLATE % b for b in blobs) + '\n'
    return ''.join(lines)


def main():
    AUTOBODY = 'autobody.tex'  # deals with \lycharlink{tag}{name} in \lyblob's
    CHARACTERS = 'characters.tex'
    CHARACTERS_OUT = 'autocharacters.tex'
    ENCODING = 'utf-8'
    with io.open(AUTOBODY, encoding=ENCODING) as fin:
        body = fin.read()
    with io.open(CHARACTERS, encoding=ENCODING) as fin:
        characters_content = fin.read()

    label_blobs = get_label_blobs(body)
    auto_characters_content = append_annotations(characters_content, label_blobs)

    with io.open(CHARACTERS_OUT, 'w', encoding=ENCODING) as fout:
        fout.write(auto_characters_content)


if __name__ == '__main__':
    sys.exit(main())

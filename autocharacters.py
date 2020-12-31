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


def get_charname_blobs(content):
    '''Return a dict of character names to lists of blob labels.'''
    CHAPTER_PREFIX = r'\chapter'
    BLOB_PREFIX = r'\lyblob'
    BLOB_TEMPLATE = '%d.%d'
    CHARNAME_PAT = re.compile(r'\\lycharlink\{(.+?)\}\{.+?\}')
    chapter_count = 0
    blob_count = 0

    lines = content.splitlines(True)
    c2bs = {}
    for line in lines:
        if line.lstrip().startswith(CHAPTER_PREFIX):
            chapter_count += 1
            blob_count = 0
        elif line.lstrip().startswith(BLOB_PREFIX):
            blob_count += 1
            left = content.index(line)
            assert content[left + len(line):].find(
                line  # no duplicate \lyblob lines except one case
            ) == -1 or '子曰：“巧言令色，鲜矣仁。”' in line
            title = extract_blob_title(content[left:])
            mats = CHARNAME_PAT.finditer(title)
            if mats:
                blob = BLOB_TEMPLATE % (chapter_count, blob_count)
                # if blob == BLOB_TEMPLATE % (11, 3):  # skip 四科十哲
                #     continue
                for m in mats:
                    charname = m.group(1)
                    if charname not in c2bs:
                        c2bs[charname] = [blob]
                    else:
                        if blob not in c2bs[charname]:
                            c2bs[charname].append(blob)
    return c2bs


def append_annotation(seg, annotation):
    insert_pos = len(seg)
    while seg[insert_pos - 1].isspace():
        insert_pos -= 1
    return seg[:insert_pos] + annotation + seg[insert_pos:]


def append_annotations(content, charname_blobs):
    removecomment_pat = re.compile(r'(?<!\\)%.+', re.M)
    content = removecomment_pat.sub('', content)

    charlabel_pat = re.compile(r'(?:^\\lypdfbookmark)|(?:^\\lylabel\{(\w+)\})',
                               re.M)
    skip_labels = set(('zisi', 'shaogong', 'boyi', 'lijiliyun'))
    segs = []
    pos = 0
    label, copy = '', True
    for mat in charlabel_pat.finditer(content):
        start = mat.start()
        seg = content[pos:start]
        pos = start
        if copy:
            segs.append(seg)
        else:
            blobs = charname_blobs[label]
            annotation = ' ' + ' '.join(r'\lyref{%s}' % b for b in blobs)
            segs.append(append_annotation(seg, annotation))
        if mat.group() == r'\lypdfbookmark':
            copy = True
            continue
        label = mat.group(1)
        if label in skip_labels:
            copy = True
            skip_labels.remove(label)
        else:
            copy = False
    seg = content[pos:]
    if copy:
        segs.append(seg)
    else:
        blobs = charname_blobs[label]
        annotation = ' ' + ' '.join(r'\lyref{%s}' % b for b in blobs)
        segs.append(append_annotation(seg, annotation))
    assert not skip_labels
    return ''.join(segs)


def main():
    AUTOBODY = 'autobody.tex'  # parse \lycharlink{tag}{name} in \lyblob's
    CHARACTERS = 'characters.tex'
    CHARACTERS_OUT = 'autocharacters.tex'
    ENCODING = 'utf-8'
    with io.open(AUTOBODY, encoding=ENCODING) as fin:
        body = fin.read()
    with io.open(CHARACTERS, encoding=ENCODING) as fin:
        characters_content = fin.read()

    charname_blobs = get_charname_blobs(body)
    auto_characters_content = append_annotations(characters_content,
                                                 charname_blobs)

    with io.open(CHARACTERS_OUT, 'w', encoding=ENCODING) as fout:
        print(auto_characters_content, file=fout)


if __name__ == '__main__':
    sys.exit(main())

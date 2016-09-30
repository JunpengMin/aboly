# coding: utf-8

from __future__ import unicode_literals
import io
import re

from rawblobs import rawblobs


ENCODING = 'utf-8'


def validate_lylabels(log):
    infiles = (
        'aboly.tex',
        'autobody.tex',
        'autocharacters.tex',
        'autotopics.tex',
        # 'guide.tex',  # TODO: uncomment
        'license.tex',
        'preface.tex',
        'references.tex',
        'usage.tex',
    )
    label_pat = re.compile(r'\\lylabel\{(.+?)\}')
    labelinfo = []  # label, infile index, line no
    for i, infile in enumerate(infiles):
        lines = io.open(infile, encoding=ENCODING).readlines()
        for l, line in enumerate(lines):
            mat = label_pat.search(line)
            if mat:
                labelinfo.append((mat.group(1), i, l))
    labelinfo.sort(key=lambda x: x[0])

    # Check for duplicates.
    nlabel = len(labelinfo)
    if nlabel != len(set(x[0] for x in labelinfo)):
        i = 0
        while i < nlabel-1:
            j = i + 1
            if labelinfo[i][0] != labelinfo[j][0]:
                i += 1
                continue
            while j < nlabel and labelinfo[i][0] == labelinfo[j][0]:
                j += 1
            if labelinfo[i][0] == labelinfo[j][0]:
                j += 1
            log.error('Duplicate lylabel "%s" in', labelinfo[i][0])
            for x in range(i, j):
                log.error('  line %d of %s', labelinfo[x][2]+1, infiles[labelinfo[x][1]])
            i = j
        return False

    # Labels should not start with a digit (reserved for \lyblob).
    for i, info in enumerate(labelinfo):
        label = info[0]
        if not label or label[0].isdigit():
            log.error('Invalid lylabel "%s" on line %d of %s',
                    label, labelinfo[i][2]+1, infiles[labelinfo[i][1]])
            return False
    return True


def validate_lylinks(log):
    infiles = (
        'autotopics.tex',
        'body.tex',
        'characters.tex',
        # 'guide.tex',  # TODO: uncomment
        'license.tex',
        'preface.tex',
        'references.tex',
        'usage.tex'
    )
    pat_anchor = re.compile(r'\\lylabel\{(.+?)\}')
    pat_link = re.compile(r'\\(?:lycharlink|lylink|lyref)\{(.+?)\}')

    anchors = set()
    for infile in infiles:
        for lineno, line in enumerate(io.open(infile, encoding=ENCODING)):
            lineno += 1
            for x in pat_anchor.finditer(line):
                anchors.add(x.group(1))
    blob_labels = set(b[0] for b in rawblobs)
    anchors |= blob_labels

    valid = True
    for infile in infiles:
        for lineno, line in enumerate(io.open(infile, encoding=ENCODING)):
            for x in pat_link.finditer(line):
                target = x.group(1)
                if target not in anchors:
                    valid = False
                    log.error('Invalid target: "%s" on line %d of "%s"', target, lineno+1, infile)
    return valid


def validate_lyrefs(log):
    infiles = (
        'body.tex',
        # 'guide.tex',  # TODO: uncomment
        'license.tex',
        'preface.tex',
        'references.tex',
        'usage.tex',
    )
    special_lyrefs = set((
        r'问\lylink{zhi4d',
    ))
    special_lyqs = set((
        '吾不试，故艺',
        '君子无众寡，无小大',
        '君子疾夫舍曰',
    ))
    labels, texts = zip(*rawblobs)
    lyref_tag = r'\lyref'
    # Ensure that \lyref is properly surrounded. Generate warnings.
    delims = r' （）【】。，、：；！—{}'
    re_lyref_before = re.compile(r'(?<![%s])\\lyref\{[0-9.]+?\}' % delims)
    re_lyref_after = re.compile(r'\\lyref\{[0-9.]+?\}(?![%s])' % delims)
    # Ensure that \lyref is properly structed.
    re_lyref_lyq = re.compile(r'\\lyref\{([\d\.]+)\}(?:\s*\\lyq\{(.+?)\})?')

    errors = 0
    for infile in infiles:
        with io.open(infile, encoding=ENCODING) as f:
            lines = f.readlines()
        for lineno, line in enumerate(lines):
            if lyref_tag in line:
                mat = re_lyref_before.search(line)
                if mat and mat.start() != 0:
                    log.warning(r'\lyref before may be incorrect on line %d of %s', lineno+1, infile)
                mat = re_lyref_after.search(line)
                if mat and mat.end() != len(line)-1:
                    log.warning(r'\lyref after may be incorrect on line %d of %s', lineno+1, infile)

                mat = re_lyref_lyq.search(line)
                if not mat:
                    log.error(r'Incorrect \lyref structure on line %d of %s', lineno+1, infile)
                    errors += 1
                else:
                    label, text = mat.group(1), mat.group(2)
                    try:
                        index = labels.index(label)
                    except ValueError:
                        log.error(r'Incorrect \lyref label on line %d of %s', lineno+1, infile)
                        errors += 1
                    else:
                        if text and text not in special_lyrefs:
                            if text.endswith('。'):
                                text = text[:-1]
                            snippets = text.split('……')
                            if any(s not in texts[index] for s in snippets):
                                if any(s in text for s in special_lyqs):
                                    continue
                                log.error(r'Incorrect \lyref quoted text on line %d of %s', lineno+1, infile)
                                log.error(text)
                                log.error(texts[index])
                                errors += 1
    return errors == 0


def validate_lywords(log):
    infiles = (
        'aboly.tex',
        'autotopics.tex',
        'body.tex',
        'characters.tex',
        'cover.tex',
        'coverly.tex',
        # 'guide.tex',  # TODO: uncomment
        'license.tex',
        'preface.tex',
        'references.tex',
        'usage.tex',
    )
    lywords = set(('lyceum', 'lychee', 'lye', 'lying', 'lying-in', 'lyings-in',
        'lymph', 'lymphatic', 'lymphocyte', 'lymphoid', 'lymphoma', 'lynch',
        'lyncher', 'lynching', 'lynx', 'lynx-eyed', 'lyre', 'lyric', 'lyrical',
        'lyrically', 'lyricism', 'lyricist', 'lyrics',
        'lyblobitemize', 'lyitemize', 'lyenumerate', 'lyquotepoem', 'lyquotepoeme', 'lyquotepara', 'lytextbackground'))  # custom words
    re_lycmd = re.compile(r'\b(ly[a-z]*)', re.I)

    valid = True
    for infile in infiles:
        for lineno, line in enumerate(io.open(infile, encoding=ENCODING)):
            for mat in re_lycmd.finditer(line):
                if mat.start() > 0 and line[mat.start() - 1] == '\\':
                    continue
                word = mat.group(1).lower()
                if word not in lywords:  # TODO: consider plurals
                    valid = False
                    log.error('Invalid lycommand: "%s" on line %d, column %d of "%s"', word, lineno+1, mat.start()+1, infile)
    return valid


def validate_pinyin(log):
    infiles = (  # NOTE: exclude covers
        'aboly.tex',
        'body.tex',
        'characters.tex',
        'autotopics.tex',
        # 'guide.tex',  # TODO: uncomment
        'license.tex',
        'preface.tex',
        'references.tex',
        'usage.tex',
    )
    tone_chars = set('āáǎàōóǒòēéěèīíǐìūúǔùüǖǘǚǜ')
    pinyin_chars = tone_chars.union(' abcdefghijklmnopqrstuwxyz')
    prefix = r'\lypy{'
    suffix = r'}'
    prefix_len = len(prefix)
    special_pinyin = set(('The Rubáiyát of Omar Khayyám',))

    for infile in infiles:
        with io.open(infile, encoding=ENCODING) as f:
            lines = f.readlines()
        for lineno, line in enumerate(lines):
            for tc in tone_chars:
                index = 0
                while True:
                    index = line.find(tc, index)
                    if index == -1:
                        break
                    valid = True
                    left = line[:index].rfind(prefix)
                    if left == -1:
                        valid = False
                    else:
                        right = line.find(suffix, index+1)
                        if right == -1:
                            valid = False
                        else:
                            pinyin = line[left + prefix_len: right]
                            valid = all(c in pinyin_chars for c in pinyin)
                    if not valid:
                        if not any(sp in line for sp in special_pinyin):
                            log.error('Incorrect pinyin on line %d, column %d of %s', lineno+1, index+1, infile)
                            return False
                        break
                    else:
                        index = right
    return True


# All above.
validators = (
    validate_lylabels,
    validate_lylinks,
    validate_lyrefs,
    validate_lywords,
    validate_pinyin,
)

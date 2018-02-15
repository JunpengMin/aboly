# coding: utf-8

from __future__ import unicode_literals, print_function
import io
import os
import pinyin  # for sorting keywords with same count of occurrences
import re
import sys


BODY = 'body.tex'
TOPICS = 'topics.tex'
AUTOTOPICS = 'autotopics.tex'
#SUMMARY = 'topics.txt'
ENCODING = 'utf-8'
INSERSION_POINT = 'INSERSION_POINT'
TOPIC_TEMPLATE = '\\lytopic{%s}（%d章）：%s\n\n'
SHORT_TOPICS_TEMPLATE = '%d章：%s\n\n'
SHORT_TOPIC_T = '\\lytopic{%s} %s'
SHORT_TOPIC_THRESHOLD = 3
SHORT_TOPICS_SEP = r'\quad '


# Retain tones.
# NOTE: As of pinyin v0.4.0, pinyin.get() defaults to get pinyin with tones, so hack_pinyin()
# is essentially useless. But unfortunately, '尚书' would be incorrectly ordered before '善人',
# using 'cháng' for '尚'. hack_pinyin() happens to circumvent this issue, so let's keep it.
def hack_pinyin():
    dat = os.path.join(os.path.dirname(pinyin.__file__), "Mandarin.dat")
    pinyin.pinyin.pinyin_dict = {}
    with io.open(dat) as f:
        for line in f:
            k, v = line.strip().split('\t')
            pinyin.pinyin.pinyin_dict[k] = v.lower().split(" ")[0]  # don't strip tones


def extract_topics():
    CHAPTER_PREFIX = r'\chapter'
    BLOB_PREFIX = r'\lyblob'
    BLOB_TEMPLATE = '%d.%d'
    pat = re.compile(r'\\lytopics\{(.*?)\}\s*(?:%.*)?')
    kwd = r'\lytopics'  # double-check
    sep = '，'

    chapter_count = 0
    blob_count = 1  # incremented after seeing BLOB_PREFIX
    match_count = 0
    topics = {}
    with io.open(BODY, encoding=ENCODING) as fin:
        content = fin.read()
    for lineno, line in enumerate(content.splitlines()):
        if line.startswith(CHAPTER_PREFIX):
            chapter_count += 1
            blob_count = 1
        elif line.startswith(BLOB_PREFIX):
            blob_count += 1

        mat = pat.match(line.strip())
        if not mat:
            if kwd in line:
                print('Malformatted line:', line, file=sys.stderr)
        else:
            match_count += 1
            blob_label = BLOB_TEMPLATE % (chapter_count, blob_count)
            if not mat.group(1):
                print('Line %d is an empty keyword list' % (lineno+1), line, file=sys.stderr)
                continue
            for c in mat.group(1).split(sep):
                if c not in topics:
                    topics[c] = [blob_label]
                else:
                    topics[c].append(blob_label)
    totalblobs = content.count(BLOB_PREFIX)
    if match_count != totalblobs:
        print('Found %d keyword lists for %d blobs' % (match_count, totalblobs))
    return topics


topic_labels = {
    # For cover links.
    '君子': 'topicjunzi',
    '仁': 'topicren2',
    '礼': 'topicli3',
    '学': 'topicxue2',
    '政': 'topiczheng4',

    '孝': 'topicxiao4',
    '义': 'topicyi4',
    '信': 'topicxin4',
    '友': 'topicyou3',
    '恕': 'topicshu4',

    '敬': 'topicjing4',
    '谦': 'topicqian1',
    '温': 'topicwen1',
    '耻': 'topicchi3',

    '文': 'topicwen2',
    '音乐': 'topicyinyue',  # 乐
    '智': 'topiczhi4a',
    '志': 'topiczhi4',

    '德': 'topicde2',
    '忠': 'topiczhong1',
    '用人': 'topicyongren',  # 贤
    '惠': 'topichui4',
    '廉': 'topiclian2',

    # Others.
    '未见': 'topicweijian',
    '快乐': 'topickuaile',
    '人我': 'topicrenwo',
    '孔子自评': 'topickongziziping',
    '人评孔子': 'topicrenpingkongzi',
}


def dump_topics(topics):
    BLOB_REF = r'\lyref{%s}'
    sorted_counts = [(k, len(v)) for k, v in topics.items()]
    sorted_counts.sort(key=lambda x: x[1], reverse=True)
    # Sort equal-count items by pinyin.
    start, stop, end = 0, 1, len(sorted_counts)
    while stop < end:
        while stop < end and sorted_counts[start][1] == sorted_counts[stop][1]:
            stop += 1
        if stop - start > 1:
            segment = sorted_counts[start:stop]
            segment.sort(key=lambda x: pinyin.get(x[0]))
            sorted_counts[start:stop] = segment
        start, stop = stop, stop+1

    # Dump topics.
    with io.open(TOPICS, encoding=ENCODING) as fin:
        template = fin.read()
    with io.open(AUTOTOPICS, 'w', encoding=ENCODING) as fout:
        insersion = template.index(INSERSION_POINT)
        prolog, epilog = template[:insersion], template[insersion+len(INSERSION_POINT):]
        fout.write(prolog)
        for i, x in enumerate(sorted_counts):
            k, v = x
            if v <= SHORT_TOPIC_THRESHOLD:
                break
            topic = TOPIC_TEMPLATE % (
                k, v,
                ' '.join(
                    BLOB_REF % v for v in topics[k]))
            if k in topic_labels:
                topic = '\\lylabel{%s}\n%s' % (topic_labels[k], topic)
            fout.write(topic)
        # Short topics.
        sclen = len(sorted_counts)
        while i < sclen:
            count = sorted_counts[i][1]
            sts = []
            while i < sclen and sorted_counts[i][1] == count:
                k = sorted_counts[i][0]
                sts.append(SHORT_TOPIC_T % (k, ' '.join(BLOB_REF % v for v in topics[k])))
                i += 1
            line = SHORT_TOPICS_TEMPLATE % (count, SHORT_TOPICS_SEP.join(sts))
            fout.write(line)
        fout.write(epilog)

#    # Dump summary.
#    summary = '\n'.join('%s\t%d' % (v[0], v[1]) for v in sorted_counts)
#    with io.open(SUMMARY, 'w', encoding=ENCODING) as f:
#        f.write(summary)


def main():
    hack_pinyin()
    topics = extract_topics()
    dump_topics(topics)


if __name__ == '__main__':
    sys.exit(main())

# coding: utf-8

from __future__ import unicode_literals
import io
import re
import sys
import subprocess


__all__ = ['titles', 'rawblobs', 'rawblobs0']

titles = None

# [('1.1', '...'), ...], without titles.
rawblobs = None

# Chinese characters only, without punctuation marks.
# sum(len(b[1]) for b in rawblobs0) -> 15915
rawblobs0 = None


def init_rawblobs():
    global titles, rawblobs, rawblobs0
    titles = []
    rawblobs = []
    rawblobs0 = []
    INFILE = 'autolybody.tex'
    ENCODING = 'utf-8'
    lytitle_re = re.compile(r'\\chapter{(.+?)}')
    lyblobraw_re = re.compile(r'\\lyblobraw\{(.+?)\}|\chapter\{', re.S)

    if subprocess.call([sys.executable, 'autolybody.py']) != 0:
        raise RuntimeError('Failed to generate %s' % INFILE)

    with io.open(INFILE, encoding=ENCODING) as fin:
        content = fin.read()

    for mat in lytitle_re.finditer(content):
        titles.append(mat.group(1))

    chapter = 0
    section = 0
    for mat in lyblobraw_re.finditer(content):
        b = mat.group(1)
        if b:
            section += 1
            rawblobs.append(('%d.%d' % (chapter, section), b))
        else:
            chapter += 1
            section = 0

    # Remove punctuation marks. Boundaries are manually picked. See below.
    LOW, HIGH = ord(u'一'), ord(u'龟')
    for b in rawblobs:
        label, text = b
        arr = []
        for c in text:
            if LOW <= ord(c) <= HIGH:
                arr.append(c)
        rawblobs0.append((label, ''.join(arr)))


init_rawblobs()


# All characters sorted:
# —‘’“”、。《》一七万丈三上下不与专且世丘东两丧中临为主举乃久义之乎乐乘九乞也
# 习乡书乱予争事二于云互五井亚亟亡亢交亦产亩享亲亵人亿仁仆今仍从仕他仞代令以仪仰仲
# 任伊伐众优会传伤伦伯似位体何余佚佛作佞佩佾使侃侍侗依侧侮侯便俎保俟信俨俭修俱倍倚
# 借倦倩倾偃偏偲偷傩僎儒允兄先克免兕党兢入八公六兮共关兴兵其具兹养兼兽内冉再冕军农
# 冠冢冯冰冶凋几凤凶出击刀分切刑列则刚创利别到前割力劝功加务动助劳勃勇勉勤勿匏北匡
# 匹区医匿十千升半华卑卒卓南博卞占卫危即卷卿历厉厌厚原厩去参又及友反发叔取受变口古
# 叩只召可台史右叶司叹各合吉吊同名后君吝否听启吴吾告呜周味呼命和咎咏咨哀哂哉哭唐唯
# 商善喜喟喭喻嗅嘉器噫四回因困固国图圃圉土圣在圭地均坏坐坚坠坦坫城域堂堪塞墙壤士壮
# 声处备复夏夕多夜大天太夫夭失夷夺奔奚奡奢奥女奴好如妇妻始姓姜威媚子孔存孙孝孟季孤
# 学孰孺宁守安宋完宗官定宜宝实审客室宪宫宰害宴家容宽宾宿寄富寒寝察寡寮对寿封射将尊
# 小少尔尚尝尤尧就尸尹尺尼尽居屏屡履山岁岂崇崔崩巍川州工左巧巫己已巷巽市布帅师希帛
# 帝带席帷常干平年并幸幼庄应庙府废度庭庶康庸庾廉廋廷开异弃弈弋式弑弓弗弘弟张弥弦归
# 当彬彭彻彼往征径待徒得徙御循微德徼心必忍志忘忠忧忮念忽忿怀怃怍怒思怡急性怨怪总恂
# 恐恒恕恭息恶恸悔患悱悲悾情惑惜惟惠惧惮惰愆愈愉意愚愠愤愬愿慈慎慝慢慧憎憾懿戈戎戏
# 成我戒或战戚戮户戾所手才托执扫扰扶承抑折报拒拖拜择拱持指挚损据授掌探接揖揭摄摈撤
# 播撰攘改攻放政故敏救教敛敝敢散敬数文斐斗斯新方施旅族无既日旧旨时昆明易昔星春昭是
# 昼晋晏晨景暇暑暴曰曲更曾月有朋服朔朕望朝期木未末本朱朽杀权杇材杖杞束来松枉析枕林
# 果枨柏某柔柙柳柴树栖栗校格桀桑桓桴梁梦棁棘棣棺椁植椟楚樊次欲欺歌止正武死殆残殖殡
# 殷殿毁毅毋母每比氏民气水永求汉汤汶沂沐沛沟没沮河治沽法泛泥泰洁洋洒津洫流浅济浮浴
# 海浸涂涅润淫深清渊渎温游溺滔滕滥漆澹灌火灭灵灶点烈焉焕焚然熟燕燧爱父片版牖牛牟牡
# 牢物犁犬犯犹狂狄狎狐独狱狷猛献玄率玉王琏琢瑚瑟瓜瓢甘甚生用甫由申画畏畔畜疏疑疚疾
# 病白百皆皇皋皙皦皮盈益盍监盖盗盛目直相盼省瞻瞽矜矢矣知矩短石硁磋磨磬磷示礼社祇祝
# 神祭祷禄禘禹离禽秀私秉科秦称移稷稻稼穆穷空穿突窃窒窥窬立章童竭端笃笑笾等答策筲简
# 箕算管箪篑类粟粪粮精系素紫絺緅纠红纣约纯纲纳纵绀绁绅细终绎经绘给绚绝绞绤绥继绰维
# 缁缊缧缭缺罔罕罚罢罪羊美羔羞群羹羽羿翔翕翼老者而耕耦耰耳耻聚聪肆肉肤肥肩肱肸胜胫
# 能脍脩脯腥臣臧自臭至致臾舆舌舍舜舞舟良色艺节芸苗苟若荆草荏荐荡荣药荷莅莒莞莫获菜
# 菲萧葬葸蒉蒙蓧蔡蔽薄薛薨藏藻蘧虎虐虑虚虞虽蛮血行衡衣表衰衽袂袍袗被裁裘裨裳襁襄襜
# 西要覆见观视觉觌角觚言訚誉譬讦讨让讪议讱讲讷论讼证识诈诔试诗诚诛诬语诱诲说诵请诸
# 诺读谁谄谅谋谌谏谓谤谨谮谲谷豆豚豹貉貊貌贞负贡责贤败货质贪贫贯贰贱贵费贼贾赉赋赏
# 赐赤赦赵起趋足路践踖踧蹈蹜躁躩身躬軏輗车轻辂辅辍辞辟辨辰辱达迁迂迅过近进远违连迟
# 迩述迷迹追退送适逆选通逝逞速造逮逸逾遂遇道遗邑邦邪邻郁郑鄙鄹酒酱醯里重野量釜钓钟
# 钻铎铿错锦长门问闲间闵闻阈阙防阳阴阶阼附际陈陋降陪陵陶陷隅随隐难雅集雉雌雍雎雕雩
# 雷霸静非面鞟鞠鞭韫韶顺须顾颂颛颜颠风食餲饐饥饩饪饭饮饰饱饿馁馈馑馔首騧马驷驾骄骈
# 骍骞骥高鬼魋魏鮀鱼鲁鲜鲤鸟鸡鸣麑麻黄黍默黜黻鼓鼗齐齿龟！，：；？

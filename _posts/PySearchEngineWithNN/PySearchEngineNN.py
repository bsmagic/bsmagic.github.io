import sqlite3 as sqlite
import jieba
from bloom_filter2 import BloomFilter
from bs4 import BeautifulSoup
import urllib.request
import re
from urllib.parse import urljoin
from urllib.parse import urlencode
import urllib.parse
import datetime

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', '-', '，', '。', "'", '', u'的', u'是'])

class Result():
    def __init__(self, no, score, url):
        self.no = no
        self.score = score
        self.url = url

class Crawler:
    # 初始化Crawler的类并传入数据库名称
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)
        # self.visited = BloomFilter(capacity=1000000, error_rate=0.001)
        # bloomfilter模块更新
        self.visited = BloomFilter(max_elements=1000000, error_rate=0.001)
    def __del__(self):
        self.con.close()
    def dbcommit(self):
        self.con.commit()

    def crawl(self, pages, depth=3):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    #c = urllib2.urlopen(page)
                    #request = urllib.request(url, headers=headers)    
                    c = urllib.request.urlopen(page)
                    

                except:
                    print("Could not or fail to open %s" % page)
                    continue
                html = c.read()
                soup = BeautifulSoup(html)
                self.addtoindex(page, soup)
                self.visited.add(page)  # 加入布隆过滤器
                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        url = url.split('<')[0]
                        url = url.split('#')[0]
                        # print(url)
                        # url=urlencode(url)
                        #url=urllib.parse.quote(url,safe=":?=/")
                        url=re.sub("'","''",url)
                        if url[0:4] == 'http' and not self.isindexedbloom(url):
                            if self.urlfilter(url):
                                newpages.add(url)
                                linktext = self.drytext(link.text)
                                self.addlinkref(page, url, linktext)
                self.dbcommit()
            pages = newpages

    def gettextonly(self,soup):
        # 清理script标签和style标签之间的内容
        [script.extract() for script in soup.findAll('script')]
        [style.extract() for style in soup.findAll('style')]
        
        # 清理标签('<'与'>'之间包裹的所有内容)
        reg = re.compile("<[^>]*>")
        content = reg.sub('', soup.prettify()).strip()
        
        # 清除过多空格 若干个空格=>一个空格
        content = " ".join(content.split())
        return content

    # 创建数据库表
    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidn on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.con.commit()

    # 为每个网页建立索引
    def addtoindex(self, url, soup):
        if self.isindexedbloom(url):
            return
            
        print('Indexing %s' % url)
        # 获取经过预处理的HTML文本
        text = self.gettextonly(soup)
        # 分词
        words = self.separatewords(text)
        # 得到URL的id
        urlid = self.getentryid('urllist', 'url', url)



        # 将每个单词与该url关联
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) \
                values (%d,%d,%d)" % (urlid, wordid, i))


    # 辅助函数，用于获取条目的id，并且如果条目不存在，就将其加入数据库中
    def getentryid(self, table, field, value, createnew=True):
        print(">", value)
        cur = self.con.execute("select rowid from \
            %s where %s='%s'" % (table, field, value))
        res = cur.fetchone()
        # 如果条目不存在，就加入一条新数据
        if res is None:
            cur = self.con.execute("insert into %s \
                (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    def separatewords(self, text):
        seg_list = jieba.cut_for_search(text)
        result = []
        for seg in seg_list:
            if seg in ignorewords:
                continue
            else:
                result.append(seg)
        return result

    # 删除空格
    # 此处还可以优化
    # 不要把\n 删掉
    def drytext(self, text):
        text = text.strip()
        text = ' '.join(text.split())
        return text

    def isindexedbloom(self, url):
        return url in self.visited

    def urlfilter(self, url):
        return True
        matcher_1 = re.compile(r'http://movie.douban.com/top250\?start=\d+.*')
        matcher_2 = re.compile(r'^http://movie.douban.com/subject/\d+/$')
        if (matcher_1.match(url) is not None or
                    matcher_2.match(url) is not None):
            return True
        return False

    # 添加一个关联两个网页的链接,记录描述超链接的关键词
    def addlinkref(self, urlFrom, urlTo, linkText):
        fromid = self.getentryid('urllist', 'url', urlFrom)
        toid = self.getentryid('urllist', 'url', urlTo)
        cur = self.con.execute("insert into link\
            (fromid,toid) values (%d,%d)" % (fromid, toid))
        linkid = cur.lastrowid
        # 如果超链接的描述text为空的话就不添加记录
        # 若不为空，先分词，再向linkword表添加记录
        if linkText != '':
            # 拆分单词
            words = self.separatewords(linkText)
            for word in words:
                wordid = self.getentryid('wordlist', 'word', word)
                self.con.execute("insert into linkwords\
                    (wordid,linkid) values (%d,%d)" % (wordid, linkid))
        return

class Searcher:
    # 初始化Searcher的类并传入数据库名称
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname, check_same_thread=False) # 简单规避掉线程之间的冲突问题
        self.mynet = Searchnet(dbname)
        self.debug_mode = False
    def __del__(self):
        self.con.close()
    def changedebugmode(self, switch):
        self.debug_mode = switch
    def dbcommit(self):
        self.con.commit()

    def getmatchrows(self, q):
        # 构造查询的字符串的基本元素
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []
        rows=[]
        # 拆分查询query单词
        words = self.separatewords(q)
        # 删除停词
        for word in words:
            if word in ignorewords:
                words.remove(word)
        
        # 统计是几张表联合查询
        tablenumber = 0
        
        for word in words:
            # 获取单词的ID，如果单词不在wordlist中则忽略
            wordrow = self.con.execute(
                "select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow is not None:
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
                tablenumber += 1
        if tablenumber==0:
            return rows, wordids    
        # 根据各个分组，建立查询
        fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
        try:
            cur = self.con.execute(fullquery)
        except IOError:
            print(fullquery)
        else:
            print(fullquery)
        rows = [row for row in cur]
        return rows, wordids    

    def query(self, q):
        # rows 查询到的相关网页集合 
        rows, wordids = self.getmatchrows(q)
        # 计算url总分
        scores = self.getscorelist(rows, wordids)
        # 排序展示
        rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
        for i, (score, urlid) in enumerate(rankedscores[0:10]):
            print('%d %f\t%s' % (i, score, self.geturlname(urlid)))

    def getQuery(self, q):
        arrResults=[]
        # rows 查询到的相关网页集合 
        rows, wordids = self.getmatchrows(q)
        if not rows:
            return arrResults
        # 计算url总分
        scores = self.getscorelist(rows, wordids)
        # 排序展示
        rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
        for i, (score, urlid) in enumerate(rankedscores[0:10]):
            #print('%d %f\t%s' % (i, score, self.geturlname(urlid)))
            result=Result(no=i, score=score, url=self.geturlname(urlid))
            arrResults.append(result)
        return arrResults

    def separatewords(self, text):
        seg_list = jieba.cut_for_search(text)
        result = []
        for seg in seg_list:
            if seg in ignorewords:
                continue
            else:
                result.append(seg)
        return result

    def getscorelist(self, rows, wordids):
        totalscores = dict([(row[0], 0) for row in rows])
        # 各类评价函数
        weights = [(1.0, self.frequencyscore(rows)),
                (1.0, self.locationscore(rows)),
                (1.0, self.distancescore(rows)),
                (1.0, self.inboundlinkscore(rows)),
                # (1.0, self.linktextscore(rows, wordids)),
                # (1.0, self.nnscore(rows,wordids))
                ]
        
        # 加权计算总分
        for (weight, scores) in weights:
            for url in totalscores:
                totalscores[url] += weight * scores[url]
        return totalscores
    # 归一化函数
    def normalizescore(self, scores, smallIsBetter = 0):
        vsmall = 0.0001  # 避免被0整除
        if smallIsBetter:
            minscore = min(scores.values())
            return dict([(u, float(minscore) / max(vsmall, l)) for (u, l) \
                        in scores.items()])
        else:
            maxscore = max(scores.values())
            if abs(maxscore - 0) < 1e-4:
                maxscore = vsmall
            return dict([(u, float(c) / maxscore) for (u, c) in scores.items()])


    # 单词频度 Word Frequency
    # rows 查询到的相关网页集合 (urlid,w0.location,w1.location,w2.location)
    # counts 记录的是
    # w0 出现的词频 + w1 出现的词频 + .... wN 出现的词频
    def frequencyscore(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows:
            counts[row[0]] += 1
        return self.normalizescore(counts)

    # 文档位置
    # 记录所有关键词的位置索引的和loc
    # loc越小认为相关性越强
    def locationscore(self, rows):
        locations = dict([(row[0], 10000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]: locations[row[0]] = loc
        return self.normalizescore(locations, smallIsBetter=1)

    # 单词距离
    # 词与词之间的位置差的绝对值的和
    # 越小越好
    def distancescore(self, rows):
        # 如果仅有一个单词，则得分都一样
        if len(rows[0]) <= 2: return dict([(row[0], 1.0) for row in rows])
        # 初始化字典
        mindistance = dict([(row[0], 10000000) for row in rows])
        for row in rows:
            dist = sum(abs(row[i] - row[i - 1]) for i in range(2, len(row)))
            if dist < mindistance[row[0]]: mindistance[row[0]] = dist
        return self.normalizescore(mindistance, smallIsBetter=1)

    # 简单统计指向该页面的连接数
    def inboundlinkscore(self, rows):
        uniqueurls = set([row[0] for row in rows])
        inboundcount = dict([(u, self.con.execute(
            'select count(*) from link where toid=%d' % u).fetchone()[0]
                            ) for u in uniqueurls])
        return self.normalizescore(inboundcount)

    def calculatepagerank(self, iterations=20):
        # 清除当前的 PageRank 表
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key,score)')
        # 初始化每个url，令其PageRank值为1
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.dbcommit()
        for i in range(iterations):
            print ("Iterations %d" % i)
            for (urlid,) in self.con.execute('select rowid from urllist'):
                # 设置PageRank最小值
                pr = 0.15
                # 循环遍历指向当前网页的所有其他网页
                for (linker,) in self.con.execute('select distinct fromid  from link where toid=%d' % urlid):
                    # 得到链接源对应网页的 PageRank值
                    linkingpr = self.con.execute(
                        "select score from pagerank where urlid=%d" % linker).fetchone()[0]
                    # 根据链接源，求得总的链接数
                    linkingcount = self.con.execute(
                        "select count(*) from link where fromid=%d" % linker).fetchone()[0]
                    pr += 0.85 * (linkingpr / linkingcount)
                # 更新 PageRank值
                self.con.execute(
                    "update pagerank set score=%f where urlid=%d" % (pr, urlid))
            # 每轮迭代结束commit一次
            self.dbcommit()

    # 从链接文本中抽取有效信息
    def linktextscore(self, rows, wordids):
        linkscores = dict([(row[0], 0) for row in rows])
        for wordid in wordids:
            cur = self.con.execute('select link.fromid,link.toid from\
            linkwords,link where wordid=%d and linkwords.linkid=link.rowid\
            ' % wordid)
            # 显然有时 cur 可能是 None
            # 如果无匹配的查询结果
            if cur is None:
                return linkscores
            for (fromid, toid) in cur:
                if toid in linkscores:
                    pr = self.con.execute('select score from pagerank where urlid\
                        =%d' % fromid).fetchone()[0]
                    linkscores[toid] += pr
        return self.normalizescore(linkscores)
    # 根据 urlid 查询url
    def geturlname(self, urlid):
        return self.con.execute(
            "select url from urllist where rowid=%d" % urlid).fetchone()[0]

    # 神经网络评价指标
    def nnscore(self, rows, wordids):
        # 获得一个由唯一的URL ID构成的有序列表
        urlids = [urlid for urlid in set([row[0] for row in rows])]
        nnres = self.mynet.getresult(wordids, urlids)
        scores = dict([(urlids[i], nnres[i]) for i in range(len(urlids))])
        return self.normalizescore(scores)

    # 简易PageRank
    def calculatepagerank(self, iterations=20):
        # 清除当前的 PageRank 表
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key,score)')

        # 初始化每个url，令其PageRank值为1
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.dbcommit()

        for i in range(iterations):
            print ("Iterations %d" % i)

            for (urlid,) in self.con.execute('select rowid from urllist'):

                # 设置PageRank最小值
                pr = 0.15

                # 循环遍历指向当前网页的所有其他网页
                for (linker,) in self.con.execute('select distinct fromid  from link where toid=%d' % urlid):
                    # 得到链接源对应网页的 PageRank值
                    linkingpr = self.con.execute(
                        "select score from pagerank where urlid=%d" % linker).fetchone()[0]

                    # 根据链接源，求得总的链接数
                    linkingcount = self.con.execute(
                        "select count(*) from link where fromid=%d" % linker).fetchone()[0]

                    pr += 0.85 * (linkingpr / linkingcount)

                # 更新 PageRank值
                self.con.execute(
                    "update pagerank set score=%f where urlid=%d" % (pr, urlid))

            # 每轮迭代结束commit一次
            self.dbcommit()


# -----------------------------------------------------------------------------
# 以下均为功能测试函数


# 抓取功能测试
def testcrawler():
    pagelist = ['http://blkstone.github.io/']
    crawler = Crawler('blkstone.db')
    crawler.createindextables()
    crawler.crawl(pagelist)


# 搜索功能测试
def testsearch():

    starttime = datetime.datetime.now()

    # long running
    searcher = Searcher('blkstone.db')
    searcher.calculatepagerank()
    searcher.query("社会工程学")

    endtime = datetime.datetime.now()

    print((endtime - starttime).microseconds/1000.0, 'ms')
    print((endtime - starttime).seconds, 's')


# 测试人工神经网络
def testann():
    mynet = nn.Searchnet('nn.db')
    # mynet.maketables()

    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203

    mynet.generatehiddennode([wWorld, wBank], [uWorldBank, uRiver, uEarth])

    # for c in mynet.con.execute('select * from wordhidden'):
    #     print c
    #
    # for c in mynet.con.execute('select * from hiddenurl'):
    #     print c

    mynet.trainquery([wWorld, wBank], [uWorldBank, uRiver, uEarth], uWorldBank)
    print(mynet.getresult([wWorld, wBank], [uWorldBank, uRiver, uEarth]))


# 测试神经网络训练
def testtrain():

    mynet = nn.Searchnet('nn.db')
    # mynet.maketables()

    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203

    allurls = [uWorldBank, uRiver, uEarth]

    for i in range(30):
        mynet.trainquery([wWorld, wBank], allurls, uWorldBank)
        mynet.trainquery([wRiver, wBank], allurls, uRiver)
        mynet.trainquery([wWorld], allurls, uEarth)
    print(mynet.getresult([wWorld, wBank], allurls))
    print(mynet.getresult([wRiver, wBank], allurls))
    print(mynet.getresult([wBank], allurls))
    print(mynet.getresult([wWorld], allurls))


def searchdemo():

    starttime = datetime.datetime.now()

    # long running
    searcher = Searcher('depth3.db')
    # searcher.calculatepagerank()
    searcher.query("肖申克的救赎")

    endtime = datetime.datetime.now()

    print(endtime - starttime).microseconds/1000.0, 'ms'
    print(endtime - starttime).seconds, 's'


if __name__ == '__main__':

    testsearch()
    # PyBFS.mytest3()
    # testann()
    # testtrain()
    # testcrawler()
    # classdemo()

## 神经网络部分

# -*- coding:utf-8 -*-
from math import tanh
#from pysqlite2 import dbapi2 as sqlite


def dtanh(y):
    return 1.0-y*y

class Searchnet:

    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def maketables(self):
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid,toid,strength)')
        self.con.execute('create table hiddenurl(fromid,toid,strength)')
        self.con.commit()

    # 获取权重
    def getstrength(self, fromid, toid, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        res = self.con.execute('select strength from %s where fromid=%d\
         and toid=%d' % (table, fromid, toid)).fetchone()

        if res == None:
            if layer == 0: return -0.2
            if layer == 1: return 0

        return res[0]

    # 设置权重
    def setstrength(self, fromid, toid, layer, strength):

        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        res = self.con.execute('select rowid from %s where fromid=%d \
            and toid=%d' % (table, fromid, toid)).fetchone()

        if res == None:
            self.con.execute('insert into %s (fromid,toid,strength) \
                values (%d,%d,%f)' % (table, fromid, toid, strength))
        else:
            rowid = res[0]
            self.con.execute('update %s set strength=%f where \
                rowid=%d' % (table, strength, rowid))

    def generatehiddennode(self, wordids, urls):

        if len(wordids) > 3: return None

        # 检查我们是否已经为这组单词建好了一个节点
        createkey = '_'.join(sorted([str(wi) for wi in wordids]))
        res = self.con.execute("select rowid from hiddennode \
            where create_key='%s'" % createkey).fetchone()

        # 如果没有，则建立之
        if res == None:
            cur = self.con.execute("insert into hiddennode (create_key)\
                values ('%s')" % createkey)
            hiddenid = cur.lastrowid

            # 设置默认权重
            for wordid in wordids:
                self.setstrength(wordid, hiddenid, 0, 1.0 / len(wordids))
            for urlid in urls:
                self.setstrength(hiddenid, urlid, 1, 0.1)
            self.con.commit()


    # 获取所有与检索结果相关的隐含层id
    def getallhiddenids(self, wordids, urlids):
        l1 = {}

        for wordid in wordids:
            cur = self.con.execute('select toid from wordhidden where fromid=%d' %
                                    wordid)
            for row in cur:
                l1[row[0]] = 1

        for urlid in urlids:
            cur = self.con.execute('select fromid from hiddenurl where toid=%d' %
                                   urlid)

            for row in cur:
                l1[row[0]] = 1

        return l1.keys()

    # 建立网络
    def setupnetwork(self, wordids, urlids):

        # 值列表
        self.wordids = wordids
        self.hiddenids = self.getallhiddenids(wordids, urlids)
        self.urlids = urlids

        # 节点输出
        self.ai = [1.0] * len(self.wordids)
        self.ah = [1.0] * len(self.hiddenids)
        self.ao = [1.0] * len(self.urlids)

        # 建立权重矩阵
        self.wi = [[self.getstrength(wordid,hiddenid,0)
                    for hiddenid in self.hiddenids]
                    for wordid in self.wordids]
        self.wo = [[self.getstrength(hiddenid,urlid,1)
                    for urlid in self.urlids]
                    for hiddenid in self.hiddenids]

    # 前向反馈
    def feedforward(self):

        # 查询单词是仅有的输入
        for i in range(len(self.wordids)):
            self.ai[i] = 1.0

        # 隐藏层节点的活跃程度
        for j in range(len(self.hiddenids)):
            sum = 0.0
            for i in range(len(self.wordids)):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # 输出层节点的活跃程度
        for k in range(len(self.urlids)):
            sum = 0.0
            for j in range(len(self.hiddenids)):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)

        return self.ao[:]

    # 计算神经网络输出结果
    def getresult(self,wordids,urlids):
        self.setupnetwork(wordids, urlids)
        return self.feedforward()

    # 反向传播算法
    def backpropagate(self, targets, N = 0.5 ):

        # 计算输出层误差
        output_deltas = [0.0] * len(self.urlids)
        for k in range(len(self.urlids)):
            error = targets[k] - self.ao[k]
            output_deltas[k] = dtanh(self.ao[k]) * error

        # 计算隐藏层误差
        hidden_deltas = [0.0] * len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error = 0
            for k in range(len(self.urlids)):
                error = error + output_deltas[k] * self.wo[j][k]
            hidden_deltas[j] = dtanh(self.ah[j]) * error

        # 更新输出权重
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                change = output_deltas[k] * self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change

        # 更新输入权重
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                change = hidden_deltas[j] * self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change

    # 如有必要，生成一个隐藏节点
    def trainquery(self, wordids, urlids, selecturl ):

        self.generatehiddennode(wordids, urlids)
        self.setupnetwork(wordids, urlids)
        self.feedforward()

        targets = [0.0] * len(urlids)
        targets[urlids.index(selecturl)]=1
        self.backpropagate(targets)
        self.updatedatabase()

    # 更新数据库
    def updatedatabase(self):
        # 将值存入数据库中
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.setstrength(self.wordids[i],self.hiddenids[j],0,
                                 self.wi[i][j])

        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                self.setstrength(self.hiddenids[j],self.urlids[k],1,
                                 self.wo[j][k])

        self.con.commit()




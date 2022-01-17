---
aliases:
layout: post
title: 用python打造含有简单神经网络的爬虫和搜索引擎
description:
comments:
menu:
tags: code python python3
categories:
permanent: 
excerpt: # abstract
timestamp: 202201170836
createdate: 2022-01-17
origindate: 
---

原来的代码是`Python 2`写的，要进行修改和改造，才能运行在`Python 3`上。特别是有些模块都已经过时了，需要安装新的模块来代替。

代码见 [PySearchEngineNN](PySearchEngineNN.py)


## logs

```python
import PySearchEngineNN
crawler = PySearchEngineNN.Crawler('G:/searchindex.db')
crawler.createindextables()
pages = ['http://xxx.xxx.xxx']
crawler.crawl(pages)
```

```python
# self.visited = BloomFilter(capacity=1000000, error_rate=0.001)
# bloomfilter模块更新
self.visited = BloomFilter(max_elements=1000000, error_rate=0.001)
```


```
pip install bloom-filter2
pip install beautifulsoup4
pip install jieba
```

### 查询代码


```python
import importlib
importlib.reload(PySearchEngineNN)
# import PySearchEngineNN
searcher = PySearchEngineNN.Searcher('G:/searchindex.db')
searcher.query('见面')
```

## clips


## 参考
###  一个简易搜索引擎(Python) 
[一个简易搜索引擎(Python) // Neurohazard](http://blkstone.github.io/2015/12/06/PySearchEngine/)

### BeautifulSoup
[Python3中BeautifulSoup的使用方法 - 知乎](https://zhuanlan.zhihu.com/p/28759710)
`from bs4 import BeautifulSoup`

### URLLIB2包的安装
[Python3安装与使用urllib2包之小坑 - 云+社区 - 腾讯云](https://cloud.tencent.com/developer/article/1469188)
这是因为builtwith依赖于urllib2包。但Pyhton2中的urllib2工具包，在Python3中分拆成了urllib.request和urllib.error两个包。就导致找不到包，同时也没办法安装。

代码中的方法函数也需要修改，基本就是将urllib2.xxx修改为urllib.request.xxx。

~：Python3中自带urllib

### 遗漏代码的补充-1
[一个简易搜索引擎 Python](#一个简易搜索引擎%20Python)的源代码：
[BlogSearch/PySearchEngine.py at master · BLKStone/BlogSearch](https://github.com/BLKStone/BlogSearch/blob/master/PySearchEngine.py)

### SQLite中单引号问题

这样可以避免value中包含反斜杠，逗号，句号，分号等各种符号的影响，但是如果value中包含单引号则会导致语法错误。

解决办法为将单引号都改为两个单引号即可，例如上例中如果name为mary's english，那么插入语句为：
[sqlite中插入单引号_w_xue的专栏-程序员宅基地_sqlite 单引号 - 程序员宅基地](https://www.cxyzjd.com/article/w_xue/18305753)
```sql
insert into xs_sessions values('S-02','T-01','mary''s english','icon_path_name','create_date_time','modify_date_time');
```

### URL编码
_百分号_编码（英語：Percent-encoding），又稱：_URL_编码（_URL_ encoding）是特定上下文的统一资源定位符 （_URL_）的编码机制

Python 2中
> 设置不编码的符号：
> 
>print urllib.quote("[http://neeao.com/index.php?id=1",":?=/](http://neeao.com/index.php?id=1%22,%22:?=/)")[  
> ](http://neeao.com/index.php?id=1)
> 
> [http://neeao.com/index.php?id=1](http://neeao.com/index.php?id=1) 这下就好了。

Python 3中要修改为：
 `url=urllib.parse.quote(url,safe=":?=/")`



还是有编码的转换问题： #todos

http://v.t.sina.com.cn/share/share.php?url='+encodeURIComponent(location.href)+'&appkey=3172366919&title='+encodeURIComponent('金砖国家通信部长、工业部长会议志愿者出征仪式暨集中培训会在我校顺利举办')+'

https://service.weibo.com/share/share.php?url=%27%2BencodeURIComponent%28location.href%29%2B%27%26appkey=3172366919%26title=%27%2BencodeURIComponent%28%27%E9%87%91%E7%A0%96%E5%9B%BD%E5%AE%B6%E9%80%9A%E4%BF%A1%E9%83%A8%E9%95%BF%E3%80%81%E5%B7%A5%E4%B8%9A%E9%83%A8%E9%95%BF%E4%BC%9A%E8%AE%AE%E5%BF%97%E6%84%BF%E8%80%85%E5%87%BA%E5%BE%81%E4%BB%AA%E5%BC%8F%E6%9A%A8%E9%9B%86%E4%B8%AD%E5%9F%B9%E8%AE%AD%E4%BC%9A%E5%9C%A8%E6%88%91%E6%A0%A1%E9%A1%BA%E5%88%A9%E4%B8%BE%E5%8A%9E%27%29%2B%27

还是要对单引号`'`进行转义：


```python
 url=re.sub("'","''",url)

```


参考：
[urllib.quote_my2010Sam的专栏-CSDN博客](https://blog.csdn.net/my2010Sam/article/details/9262141)

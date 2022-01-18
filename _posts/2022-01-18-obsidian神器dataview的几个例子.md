---
aliases:
layout: post
title:
description:
comments:
menu:
tags: 笔记软件 obsidian
categories:
permanent: 
excerpt: # abstract
timestamp: 202201181046
createdate: 2022-01-18
origindate: 
---

## 当日笔记列表
```dataview
TABLE file.mday, file.cday, file.day, createdate
from "logs"
where createdate=this.file.day
```

## GTD笔记列表
### Inprogress
```dataview
TABLE file.mday, file.cday, file.day, createdate, tags
from  #todos/doing
```
#todos/doing

### Maybe
```dataview
TABLE file.mday, tags
from  #todos/maybe
```

### 课诵
 ```dataview
table  taboo as 禁忌, remind AS 提醒 ,  promote as 倡导, meme as 想法
sort status desc, file.mtime desc
where taboo !=null or remind!=null or promote!=null or meme!=null or 提醒!=null
```

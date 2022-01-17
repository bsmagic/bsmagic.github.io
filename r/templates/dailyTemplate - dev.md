---
aliases: 
tags: 笔记软件
title:
timestamp: {{date:YYYYMMDD}}{{time:HHmm}}
createdate: {{date:YYYY-MM-DD}} 
---

**目录**

[toc]

# 当日笔记列表

%%列表当日相关笔记
```dataview
TABLE file.mday, file.cday
where file.mday=this.file.mday or file.cday=this.file.mday
```
%%

%%
```dataview
TABLE file.mday, file.cday
where file.mday=this.file.day
```
%%

%%
```dataview
list from "logs"
WHERE contains(file.name, "20211122")
```
%%

```dataview
TABLE file.mday, file.cday, file.day, createdate
from "logs"
where createdate=this.file.day
```

# 其他

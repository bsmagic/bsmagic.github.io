---
aliases: 
tags: 
title:
timestamp: {{date:YYYYMMDD}}{{time:HHmm}}
createdate: {{date:YYYY-MM-DD}} 
---

**目录**

[toc]

# 当日笔记列表
```dataview
TABLE file.mday, file.cday, file.day, createdate
from "logs"
where createdate=this.file.day
```

# 其他

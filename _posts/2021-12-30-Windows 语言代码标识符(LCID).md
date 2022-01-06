---
aliases:
layout: page
title:
description:
keywords:
comments:
menu:
tags:  LCID
categories:
permanent: 
excerpt:
# 摘要？
timestamp: 202112301422
createdate: 2021-12-30
---

在输出时间格式时，会遇到Windows 语言代码标识符(LCID)的问题。

**LCID**用于定义发送给浏览器的页面**地区**标识，它用以确定时间、货币、数字等的显示方式，类似于控制面板中的“区域设置”。 ^[https://baike.baidu.com/item/LCID/8432334]

操作系统的语言ID（Language Identifier）基本上等同于LCID（Locale Identifier，也叫做区域标识），可以认为两者是相同的。^[https://blog.csdn.net/norman_irsa/article/details/104213823]



## 中国大陆地区的LCID


| Locale | Language code | LCID string | LCID Decimal | LCID Hexadecimal | Codepage |
| --- | --- | --- | --- | --- | --- |
| Afrikaans | af | af | 1078 | 436 | 1252 | 
| Chinese - China |zh |zh-cn |2052|804 |
| English - United States|en|en-us|1033|409|1252

来源：^[[Language Codes](https://www.science.co.il/language/Locale-codes.php) ]

来源网站是以色列的科技目录：
Israel Science and Technology Directory – www.science.co.il
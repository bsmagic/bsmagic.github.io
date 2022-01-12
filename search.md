---
layout: page
title: Search
tags: todos  
---


## Powered by Simple-jekyll-search 
注：生成全文索引会很大？

<!-- HTML elements for search -->
<input type="text" id="search-input" placeholder="搜索博客 - 输入标题/相关内容/日期/Tags.." style="width:380px;"/>
<ul id="results-container"></ul>
<!-- script pointing to jekyll-search.js -->
<script src="/assets/simple-jekyll-search.js"></script>

<script>
SimpleJekyllSearch({
    searchInput: document.getElementById('search-input'),
    resultsContainer: document.getElementById('results-container'),
    json: '/assets/search.json',
    searchResultTemplate: '<li><a href="{url}" title="{desc}">{title}</a></li>',
    noResultsText: 'No results‘,
    limit: 20,
    fuzzy: true
  })
</script>

<style>
#search-input {
    width: 90%;
    height: 35px;
    color: #333;
    background-color: rgba(227,231,236,.2);
    line-height: 35px;
    padding:0px 16px;
    border: 1px solid #c0c0c0;
    font-size: 16px;
    font-weight: bold;
    border-radius: 17px;
    outline: none;
    box-sizing: border-box;
    box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(102,175,233,.6);
}
#search-input:focus {
    outline: none;
    border-color: rgb(102, 175, 233);
    background-color: #fff;
    box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px #007fff;
}
</style>

## Powed by Google (有延时和遗漏)
<meta name="viewport" content="width=device-width, initial-scale=1">
<div id='googlesearch'>
<script async src="https://cse.google.com/cse.js?cx=46146bed48dfe8403"></script>
<div class="gcse-search"></div>
</div>

## Powerd by lunr.js （不支持中文，支持中文的版本索引太大）

```html
{% raw %}
<form action="/search" method="get">
  <input type="text" id="search-box" name="query">
  <input type="submit" value="search">
</form>

<ul id="search-results"></ul>

<script>
  window.store = {
    {% for post in site.posts %}
      "{{ post.url | slugify }}": {
        "title": "{{ post.title | xml_escape }}",
        "author": "{{ post.author | xml_escape }}",
        "category": "{{ post.category | xml_escape }}",
        "content": "{{ post.content | strip_html | strip_newlines | jsonify }}",
        "url": "{{ post.url | xml_escape }}"
      }
      {% unless forloop.last %},{% endunless %}
    {% endfor %}
  };
</script>
<script src="/assets/lunr.min.js"></script>
<script src="/assets/search-by-lunr.js"></script>
{% endraw %}
```


## Powered by GhostBot (要后台安装，github上不支持)

```html
<script src="/assets/ghostbot.js"></script>	
<input type="text" class="search-form-input" placeholder="Search"/>
<div class="search-bar-result"></div>

<script>
var g = new GhostBot({
	inputbox: document.querySelector('.search-form-input'),
	target: document.querySelector('.search-bar-result'),
	info_template: "<h4>Find{{amount}}Articles.</h4>",
    result_template: "<a href='{{link}}' class='searchResult'>{{title}}</a>",
});
</script>
```


LunaYJ/GhostBot: A Ghost Blog Search Engine based on Ghost API, no need Lunr.js & jQuery
https://github.com/LunaYJ/GhostBot
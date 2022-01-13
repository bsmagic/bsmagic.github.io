---
layout: page
title: Search
tags: todos
---

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
    noResultsText: 'No results', 
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

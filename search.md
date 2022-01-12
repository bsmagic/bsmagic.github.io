---
layout: page
title: Search
---

## Powered by Simple-jekyll-search
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
    noResultsText: '没有搜索到文章',
    limit: 20,
    fuzzy: false
  })
</script>

## Powed by Google

<div id='googlesearch'>
<script async src="https://cse.google.com/cse.js?cx=46146bed48dfe8403"></script>
<div class="gcse-search"></div>
</div>

## Powerd by lunr.js
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
        "content": {{ post.content | strip_html | strip_newlines | jsonify }},
        "url": "{{ post.url | xml_escape }}"
      }
      {% unless forloop.last %},{% endunless %}
    {% endfor %}
  };
</script>
<script src="/assets/lunr.min.js"></script>
<script src="/assets/search.js"></script>


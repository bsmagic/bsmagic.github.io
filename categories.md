---
layout: categories
title: Categories
description: 分类页面
keywords: 分类key
comments: false
menu: 分类menu
tags: categories, page
---

## 实现方法1
<section class="container posts-content">
{% assign sorted_categories = site.categories | sort %}
{% for category in sorted_categories %}
<h3 id="{{ category[0] }}">{{ category | first }}</h3>
<ol class="posts-list">
{% for post in category.last %}
<li class="posts-list-item">
<span class="posts-list-meta">{{ post.date | date:"%Y-%m-%d" }}</span>
<a class="posts-list-name" href="{{ site.url }}{{ post.url }}">{{ post.title }}</a>
</li>
{% endfor %}
</ol>
{% endfor %}
</section>
<!-- /section.content -->

## 实现方法2
---
layout: page
permalink: /categories/
title: 博客分类
---

<!--添加搜索框-->
<br/>
<!-- HTML elements for search -->
<input type="text" id="search-input" placeholder="搜索博客 - 输入标题/相关内容/日期/Tags.." style="width:380px;"/>
<ul id="results-container"></ul>

<!-- script pointing to jekyll-search.js -->
<script src="{{ site.baseurl }}/assets/simple-jekyll-search.min.js"></script>

<script>
SimpleJekyllSearch({
    searchInput: document.getElementById('search-input'),
    resultsContainer: document.getElementById('results-container'),
    json: '/search.json',
    searchResultTemplate: '<li><a href="{url}" title="{desc}">{title}</a></li>',
    noResultsText: '没有搜索到文章',
    limit: 20,
    fuzzy: false
  })
</script>
<br/>


<div id="archives">
{% for category in site.categories %}
  <div class="archive-group">
    {% capture category_name %}{{ category | first }}{% endcapture %}
    <div id="#{{ category_name | slugize }}"></div>
    <p></p>

    <h3 class="category-head">{{ category_name }} ({{site.categories[category_name].size()}})</h3>
    <a name="{{ category_name | slugize }}"></a>
    {% for post in site.categories[category_name] %}
    <article class="archive-item">
      <h4><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h4>
    </article>
    {% endfor %}
  </div>
{% endfor %}
</div>

<!-- zoharandroid.github.io/categories.html at master · ZoharAndroid/zoharandroid.github.io
https://github.com/ZoharAndroid/zoharandroid.github.io/blob/master/categories.html-->
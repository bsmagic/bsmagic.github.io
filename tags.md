---
layout: tags
title: Tags
description: 标签页面
tags: tags, page
---


## 实现方法1

<div class="tags-expo">
  <div class="tags-expo-list">
    {% for tag in site.tags %}
    <a href="#{{ tag[0] | slugify }}" class="post-tag">{{ tag[0] }}</a>
    {% endfor %}
  </div>
  <hr/>
  <div class="tags-expo-section">
    {% for tag in site.tags %}
    <h2 id="{{ tag[0] | slugify }}">{{ tag[0] }}</h2>
    <ul class="tags-expo-posts">
      {% for post in tag[1] %}
        <a class="post-title" href="{{ site.baseurl }}{{ post.url }}">
      <li>
        {{ post.title }}
      <small class="post-date">{{ post.date | date_to_string }}</small>
      </li>
      </a>
      {% endfor %}
    </ul>
    {% endfor %}
  </div>
</div>

<!-- 為 GitHub 上的 Jekyll 添加 Tags · Rory
https://nk910216.github.io/2017/08/11/UsingTagsForJekyll/ -->


## 实现方法2


{%- capture site_tags -%}
    {%- for tag in site.tags -%}
        {{- tag | first -}}{%- unless forloop.last -%},{%- endunless -%}
    {%- endfor -%}
{%- endcapture -%}
{%- assign tags_list = site_tags | split:',' | sort -%}

{%- for tag in tags_list -%}
    <a href="#{{- tag -}}" class="btn btn-primary tag-btn"><i class="fa fa-tag" aria-hidden="true"></i>&nbsp;{{- tag -}}&nbsp;({{site.tags[tag].size}})</a>
{%- endfor -%}

<div id="full-tags-list">
{%- for tag in tags_list -%}
    <h2 id="{{- tag -}}" class="linked-section">
        <i class="fa fa-tag" aria-hidden="true"></i>
        &nbsp;{{- tag -}}&nbsp;({{site.tags[tag].size}})
    </h2>
    <div class="post-list">
        {%- for post in site.tags[tag] -%}
            <div class="tag-entry">
                <a href="{{ post.url | relative_url }}">{{- post.title -}}</a>
                <div class="entry-date">
                    <time datetime="{{- post.date | date_to_xmlschema -}}">{{- post.date | date: "%B %d, %Y" -}}</time>
                </div>
            </div>
        {%- endfor -%}
    </div>
{%- endfor -%}
</div>

<br>

参考：zoharandroid.github.io/tags.html at master · ZoharAndroid/zoharandroid.github.io
https://github.com/ZoharAndroid/zoharandroid.github.io/blob/master/tags.html

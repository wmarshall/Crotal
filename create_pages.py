#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from unipath import Path
from _models.pages import Pages
from templates import Views
import settings

author = 'dinever'

SAMPLE = """{%% extends "_layout/base.html" %%}
{%% block title %%}
%s
{%% endblock %%}
{%% block description %%}
%s
{%% endblock %%}
{%% block content %%}
<div id="index_content" class="span9">
    <div id="article">
        <h1>%s</h1>
{%% markdown %%}

请在这里写下内容，

编辑该页，请去`/source/%s/index.html`。

记得在`/source/_layout/base.html`中以你喜欢的方式加上该页的链接。（比如在导航栏中）

{%% endmarkdown %%}
    </div>
</div>

{%% endblock %%}

"""

if __name__ == '__main__':
    flag = 0
    if len(sys.argv) == 1:
        title = raw_input('页面标题/Page Title:')
        slug = raw_input('页面简写(用于URL)/Page Slug(For URL):')
        description = raw_input('页面描述(用于SEO)/Page Description(For SEO):')
        try:
            os.makedirs('source/'+slug)
        except:
            pass
        open('source/'+ slug +'/index.html', 'w+').write(SAMPLE % (title, description, title, slug))
        print 'make之后就可以去' + settings.site_url + '/' + slug + '/' + '查看新页面了。'
        print 'You can view the new page at ' + settings.site_url + '/' + slug + '/' + ' after make the site.'

    elif len(sys.argv) != 1:
        open('_posts/' + file_title, 'w+').write(new_post)
    else:
        usraccount = sys.argv[1]
        passwd = sys.argv[2]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import sys
import time
from datetime import datetime

from crotal import utils
from crotal import server
from crotal import logger
from crotal.site import Site
from crotal.config import Config
from crotal.version import __version__
from crotal.plugins.pinyin.pinyin import PinYin

LOGO = \
"""  ____ ____   ___ _____  _    _
 / ___|  _ \\ / _ \\_   _|/ \\  | |
| |   | |_) | | | || | / _ \\ | |
| |___|  _ <| |_| || |/ ___ \\| |___
 \____|_| \_\\\\___/ |_/_/   \\_\\_____|
"""


LOGO_LARGE = (
        "________________________________________",
        "|   ____ ____   ___ _____  _    _      |",
        "|  / ___|  _ \\ / _ \\_   _|/ \\  | |     |",
        "| | |   | |_) | | | || | / _ \\ | |     |",
        "| | |___|  _ <| |_| || |/ ___ \\| |___  |",
        "|  \____|_| \_\\\\___/ |_/_/   \\_\\_____| |",
        "|                                      |",
        "|          Version: {:<6s}             |".format(__version__),
        "|______________________________________|",
        )

POST_SAMPLE =\
"""---
title: "{0}"
date: {1}
categories:
slug: {2}
---

"""

PAGE_SAMPLE = \
"""---
layout: page.html
title: "{0}"
date: {1}
url: {2}
description: {3}
---

## A demo page!

This is a demo page.
"""


class Command(object):

    @staticmethod
    def locate_base_dir():
        current_dir = os.getcwd()
        while True:
            if os.path.exists(os.path.join(current_dir, '_config.yml')):
                return current_dir
            elif current_dir == os.path.dirname(current_dir):
                return None
            else:
                current_dir = os.path.dirname(current_dir)

    @staticmethod
    def load_config():
        return Config(Command.locate_base_dir())

    @staticmethod
    def generate(full=False, output=None):
        start = time.time()
        site = Site(path=Command.locate_base_dir(), full=full, output=output)
        site.generate()
        end = time.time()
        logger.info("Site generated in {0:.2f} seconds.".format(end-start))

    @staticmethod
    def init_site(site_name='crotal'):
        curr = os.path.dirname(os.path.abspath(__file__))
        site_dir = os.path.join(curr, "init")
        utils.copy_dir(site_dir, site_name)
        logger.blue_text(message=LOGO)
        logger.success('Site created.')

    @staticmethod
    def start_server(port):
        for line in LOGO_LARGE:
            logger.info(line)
        print()
        path = Command.locate_base_dir()
        server.start(port, path=path)

    @staticmethod
    def create_post(post_title='sample post'):
        config = Command.load_config()
        now = datetime.now()
        pub_time = unicode(now.strftime('%Y-%m-%d %H:%M'))
        pinyin = PinYin()
        pinyin.load_word()
        slug = pinyin.hanzi2pinyin_split(string=post_title, split='-')
        new_post = POST_SAMPLE.format(post_title.decode('utf8'), pub_time, slug)
        file_title = "{0}-{1}.markdown".format(unicode(now.strftime('%Y-%m-%d')), post_title.decode('utf8'))
        absolute_file_path = os.path.join(config.base_dir, (os.path.join(config.posts_dir, file_title)))
        if not os.path.exists(absolute_file_path):
            open(os.path.join(config.base_dir, absolute_file_path.encode('utf8')), 'w+').write(new_post.encode('utf8'))
        else:
            logger.error("File exists: {0}".format(absolute_file_path))

    @staticmethod
    def create_page():
        config = Command.load_config()
        title = logger.info_input('Page Title')
        url = logger.info_input('Page URL (.e.g, /foo/bar/):')
        description = logger.info_input('Page Description:')
        pinyin = PinYin()
        slug = pinyin.hanzi2pinyin_split(string=title, split="-")
        now = datetime.now()
        pub_date = now.strftime("%Y-%m-%d %H:%M")
        page = PAGE_SAMPLE.format(title, pub_date, url, description)
        file_path = os.path.join(config.pages_dir, "{0}.markdown".format(slug))
        open(os.path.join(config.base_dir, file_path), 'w+').write(page)
        logger.success('You can browse the page by {0} After generating the site.'.format(url))


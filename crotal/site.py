# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import md5

from crotal import db
from crotal import utils
from crotal.config import Config
from crotal.renderer import Renderer
from crotal.loader import PostLoader, PageLoader, TemplateLoader, StaticLoader


class Site(object):

    LoaderClass = [PostLoader, PageLoader, TemplateLoader, StaticLoader]

    def __init__(self, path=os.getcwd(), full=False, output='preview'):
        self.config = Config(path, output)
        if full:
            self.database = db.Database(dict(), self.config.db_path)
        else:
            self.database = db.Database.from_file(self.config.db_path)
        self.data = {}
        self.site_content = {}
        self.static_files = []
        self.loaders = []
        for Loader in self.LoaderClass:
            loader = Loader(self.database, self.config)
            loader.load(self.update_data)
            self.loaders.append(loader)

    def update_data(self, data):
        self.data.update(data)

    def generate(self):
        self.render()
        self.write()
        self.save()

    def parse_single_file(self, file_path, event_type):
        """
        This method is used when single file change was detected during the server
        running.
        """
        file_path = os.path.relpath(file_path, self.config.base_dir)
        loader = self.detect_file_type(file_path)
        loader.single_file_on_change(file_path, event_type, self.update_data)
        self.generate()

    def detect_file_type(self, file_path):
        for loader in self.loaders:
            for path in loader.path:
                if file_path.startswith(path):
                    return loader

    def render(self):
        renderer = Renderer(self.config, **self.data)
        self.site_content, self.static_files = renderer.run()

    def write(self):
        digest_table = self.database.get_table('digest')
        for path in self.site_content:
            digest = md5.md5(self.site_content[path]).hexdigest()
            output_path = os.path.join(self.config.publish_dir, path)
            if not os.path.exists(output_path) or digest != digest_table.get(path):
                utils.output_file(output_path, self.site_content[path])
                digest_table[path] = digest

    def save(self):
        self.database.save()


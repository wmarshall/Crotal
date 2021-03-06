# -*- coding: utf-8 -*
from __future__ import unicode_literals, print_function
import os

from crotal.loader import BaseLoader
from crotal.models.template import Template


class TemplateLoader(BaseLoader):
    _name = 'templates'
    _Model = Template

    @property
    def path(self):
        return [os.path.join(self.config.templates_dir)]

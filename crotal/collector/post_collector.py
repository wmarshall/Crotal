import os
import time

from ..models.posts import Post
from ..models.others import Category, Tag, Archive
from ..reporter import Reporter
from ..collector import Collector

reporter = Reporter()

class PostCollector(Collector):
    def __init__(self, current_dir, database, config):
        Collector.__init__(self)
        self.config = config
        self.database = database
        self.current_dir = current_dir
        self.posts_dir = os.path.normpath(
            os.path.join(
                self.current_dir, 'source', 'posts'))
        self.posts = []
        self.new_posts = []
        self.removed_posts = []
        self.categories = {}
        self.tags = {}
        self.archives = []
        self.posts_files = self.process_directory(self.posts_dir)
        self.page_number = 0

    def run(self):
        new_filenames, old_filenames, removed_filenames = self.detect_new_filenames('posts')
        self.parse_old_posts(old_filenames)
        self.parse_new_posts(new_filenames)
        self.parse_removed_posts(removed_filenames)
        self.posts_sort()
        self.collect_others()
        self.save_others()
        self.page_number = len(self.posts) / 5

    def collect_others(self):
        '''
        Collect categories and tags in post object list.
        '''
        self.collect_categories()
        self.collect_tags()

    def collect_categories(self):
        '''
        Collect the categories in a sigle post object.
        '''
        for post in self.posts:
            if hasattr(post, 'categories'):
                for category in post.categories:
                    if category in self.categories:
                        self.categories[category].add_post(post)
                    else:
                        self.categories[category] = Category(category)
                        self.categories[category].add_post(post)

    def collect_tags(self):
        '''
        Collect the tags in a sigle post object.
        '''
        for post in self.posts:
            if hasattr(post, 'tags'):
                for tag in post.tags:
                    if tag in self.tags:
                        self.tags[tag].add_post(post)
                    else:
                        self.tags[tag] = Tag(tag)
                        self.tags[tag].add_post(post)

    def collect_archives(self, post): # TODO
        '''
        Collect the archives in a sigle post object.
        (This method has not been used)
        '''
        Archive(post.pub_time)
        self.archives.append(Archive(post.pub_time))

    def save_others(self):
        '''
        After all of the tags is collected
        '''
        for tag in self.tags.values():
            tag.save()

    def parse_old_posts(self, filenames):
        for filename in filenames:
            post_content = self.database.get_item_content('posts', filename)
            post_tmp = Post(self.config, filename=filename)
            post_tmp.parse_from_db(post_content)
            self.posts.append(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(
                post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.posts_dir,
                    filename))
            post_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': post_dict}
            self.database.set_item('posts', filename, post_dict_in_db)

    def parse_new_posts(self, filenames):
        for filename in filenames:
            post_tmp = Post(self.config, filename=filename)
            file_content = open(os.path.join(self.posts_dir, filename),'r')\
                .read().decode('utf8')
            if not post_tmp.check_illegal(file_content, filename=filename):
                # If the post_content is not illegal, pass it.
                reporter.source_illegal('post', filename)
                continue
            else:
                post_tmp.parse()
            self.posts.append(post_tmp)
            self.new_posts.append(post_tmp)
            post_dict = post_tmp.__dict__.copy()
            post_dict['pub_time'] = time.mktime(
                post_dict['pub_time'].timetuple())
            post_dict.pop('config', None)
            last_mod_time = os.path.getmtime(
                os.path.join(
                    self.posts_dir,
                    filename))
            post_dict_in_db = {
                'last_mod_time': last_mod_time,
                'content': post_dict}
            self.database.set_item('posts', filename, post_dict_in_db)

    def remove_posts(self):
        site_dir = os.path.join(self.current_dir, '_sites')
        for post in self.removed_posts:
            dname = os.path.join(site_dir, post.url.strip("/\\"))
            filename = os.path.join(dname, 'index.html')
            try:
                os.remove(filename)
            except Exception, e:
                reporter.failed_to_remove_file('post', post.title)

    def parse_removed_posts(self, filenames):
        site_dir = os.path.join(self.current_dir, '_sites')
        for filename in filenames:
            post_content = self.database.get_item_content('posts', filename)
            post_tmp = Post(self.config, filename=filename)
            post_tmp.parse_from_db(post_content)
            self.database.remove_item('posts', filename)
            self.removed_posts.append(post_tmp)
            dname = os.path.join(site_dir, post_tmp.url.strip("/\\"))
            filename = os.path.join(dname, 'index.html')
            os.remove(filename)

    def posts_sort(self):
        self.posts.sort(key=lambda c:c.pub_time)
        self.posts.reverse()
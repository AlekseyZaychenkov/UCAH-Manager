import os

from django.test import SimpleTestCase
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table

from loader.credentials import OATH_SECRET, CONSUMER_SECRET, CONSUMER_KEY, OATH_TOKEN
from models import TumblerCredentials
from tumblr_loader import TumblrLoader
from utils import Utils

import sys
sys.path.append("..")
from models import TumblerCredentials
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


class Test_TumblrLoader(SimpleTestCase):

    def test_writing_and_reading(self):
        tmblr = TumblrLoader(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            OATH_TOKEN,
            OATH_SECRET
        )


        userInfo = (tmblr.client.info())['user']
        print(f"User info:"
          f"\nname: {userInfo['name']}"
          f"\nfollowing: {userInfo['following']}"
          f"\ndefault_post_format: {userInfo['default_post_format']}"
          f"\nlikes: {userInfo['likes']}"
          f"\nblogs: {len(userInfo['blogs'])}")


        tags = ['paleontology']
        tmblr.download(tags)
        # TODO: uncomment when TumblrLoader.get_from_blog(self, blog, tags) will be ready
        # blogs = ['https://www.tumblr.com/blog/view/alphynix']
        # tmblr.download(tags, blogs)



        # Utils.startSession()
        #
        # drop_table(TumblerCredentials)
        # sync_table(TumblerCredentials)



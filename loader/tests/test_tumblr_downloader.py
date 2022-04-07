import os

from django.test import SimpleTestCase
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
from loader.credentials import OATH_SECRET, CONSUMER_SECRET, CONSUMER_KEY, OATH_TOKEN
from tumblr_loader import TumblrLoader
from utils import Utils

import sys
sys.path.append("..")
from models import PostEntry

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


class Test_TumblrLoader(SimpleTestCase):

    def test_writing_and_reading(self):
        Utils.startSession()

        sync_table(PostEntry)
        drop_table(PostEntry)

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
                  f"\nblogs: {len(userInfo['blogs'])}"
              )


        tags = ['paleontology']
        tmblr.download(tags)
        # TODO: uncomment when TumblrLoader.get_from_blog(self, blog, tags) will be ready
        # blogs = ['https://www.tumblr.com/blog/view/alphynix']
        # tmblr.download(tags, blogs)


        pe = PostEntry.objects.all()
        pe = PostEntry.objects(originalPostId=680857344253591552)
        # print(f"pe: {pe}")
        # print(f"pe.count(): {pe.count()}")
        # print(f"type(pe): {type(pe)}")

        print("PostEntryes:")
        for instance in pe:
            print(f"<===== ===== ===== instance.id: {instance.id} ===== ===== =====>")

            print(f"instance.originalResource: {instance.originalResource}")
            print(f"instance.originalBlogName: {instance.originalBlogName}")
            print(f"instance.originalBlogUrl: {instance.originalBlogUrl}")
            print(f"instance.originalPostId: {instance.originalPostId}")
            print(f"instance.originalPostUrl: {instance.originalPostUrl}")
            print(f"instance.originalPostedDate: {instance.originalPostedDate}")
            print(f"instance.originalPostTags: {instance.originalPostTags}")
            print(f"instance.originalText: {instance.originalText}")
            print(f"instance.originalFileUrls: {instance.originalFileUrls}")
            print(f"instance.originalExternalLinkUrls: {instance.originalExternalLinkUrls}")

            print(f"instance.searchTags: {instance.searchTags}")
            print(f"instance.downloatedDate: {instance.downloatedDate}")

            print(f"instance.text: {instance.text}")
            print(f"instance.fileUrls: {instance.fileUrls}")
            print(f"instance.externalLinkUrls: {instance.externalLinkUrls}")

            print(f"instance.description: {instance.description}")
            print(f"instance.storage: {instance.storage}")

            print(f"instance.wherePosted: {instance.wherePosted}")

            print(f"<===== ===== =====  * * * * *  ===== ===== =====>\n")




        # pe = PostEntry.objects.values()
        # print("PostEntryes:")
        # for instance in pe:
        #     print(str(pe))



        # Utils.startSession()
        #
        # drop_table(TumblerCredentials)
        # sync_table(TumblerCredentials)



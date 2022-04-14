import os

from django.test import SimpleTestCase
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
from credentials import OATH_SECRET, CONSUMER_SECRET, CONSUMER_KEY, OATH_TOKEN
from settings import PATH_TO_STORE
from tumblr_loader import TumblrLoader
from utils import Utils

import sys

# from venv.bin import pytest.fixture

sys.path.append("..")
from models import PostEntry, Compilation


os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


class Test_TumblrLoader(SimpleTestCase):

    # @pytest.fixture
    # TODO: make the function fixture
    def prepare_db(self):
        Utils.startSession()

        sync_table(PostEntry)
        sync_table(Compilation)

        drop_table(PostEntry)
        drop_table(Compilation)

    # TODO: make the function fixture
    def create_parser(self):
        return TumblrLoader(
                    CONSUMER_KEY,
                    CONSUMER_SECRET,
                    OATH_TOKEN,
                    OATH_SECRET
                )

    # TODO: test method for generate_storage_patch()
    # TODO: test method for save_files()



    # TODO: create test file with response for 1 tag
    # TODO: create test file with response for 1 tag and many blogs
    # TODO: create dump file with data for 1 tag
    # TODO: create dump file with data for 1 tag and many blogs
    # TODO: create method for response and dump for 1 tag
    # TODO: create method for response and dump for 1 tag and many blogs

    def print_user_info(self, client):
        userInfo = (client.info())['user']
        print(f"My user for connection to Tumbler:"
              f"\nname: {userInfo['name']}"
              f"\nfollowing: {userInfo['following']}"
              f"\ndefault_post_format: {userInfo['default_post_format']}"
              f"\nlikes: {userInfo['likes']}"
              f"\nblogs: {len(userInfo['blogs'])}"
              )


    def test_download(self):
        self.prepare_db()
        tmblr = self.create_parser()
        self.print_user_info(tmblr.client)


        tag = 'paleontology'
        number = 20
        path = tmblr.generate_storage_patch(PATH_TO_STORE, tag)


        # tmblr.download(number, tag=tag)

        blogs = ['netmassimo', 'kinogane']
        tmblr.download(number, storagePath=path, blogs=blogs)


        pe = PostEntry.objects.all()
        pe = sorted(pe, key=lambda post: post['original_posted_timestamp'], reverse=True)


        print("PostEntryes:")
        for instance in pe:
            print(f"<===== ===== ===== instance.id: {instance.id} ===== ===== =====>")

            # print(f"instance.original_resource: {instance.original_resource}")
            # print(f"instance.original_blog_name: {instance.original_blog_name}")
            # print(f"instance.original_blog_url: {instance.original_blog_url}")
            # print(f"instance.original_post_id: {instance.original_post_id}")
            print(f"instance.original_post_url: {instance.original_post_url}")
            # print(f"instance.original_posted_date: {instance.original_posted_date}")
            # print(f"instance.original_post_tags: {instance.original_post_tags}")
            # print(f"instance.original_text: {instance.original_text}")
            print(f"instance.original_file_urls: {instance.original_file_urls}")
            print(f"instance.original_external_link_urls: {instance.original_external_link_urls}")

            # print(f"instance.search_tag: {instance.search_tag}")
            # print(f"instance.downloaded_date: {instance.downloaded_date}")

            # print(f"instance.text: {instance.text}")
            print(f"instance.file_urls: {instance.file_urls}")
            # print(f"instance.external_link_urls: {instance.external_link_urls}")
            #
            # print(f"instance.description: {instance.description}")
            # print(f"instance.storage: {instance.storage}")
            #
            # print(f"instance.where_posted: {instance.where_posted}")

            # print(f"<===== ===== =====  * * * * *  ===== ===== =====>\n")
            # print("\n")

        print("\nCompilation:")
        comps = Compilation.objects.all()
        for comp in comps:
            print(f"comp.id {comp.id}")
            print(f"comp.original_resource {comp.original_resource}")
            print(f"comp.search_tag {comp.search_tag}")
            print(f"comp.search_blogs {comp.search_blogs}")
            print(f"comp.downloaded_date {comp.downloaded_date}")
            print(f"comp.storage {comp.storage }")

            print(f"comp.post_ids {comp.post_ids}")
            print("\n")



        # pe = PostEntry.objects.values()
        # print("PostEntryes:")
        # for instance in pe:
        #     print(str(pe))
        #
        #
        #
        # Utils.startSession()
        #
        # drop_table(TumblerCredentials)
        # sync_table(TumblerCredentials)

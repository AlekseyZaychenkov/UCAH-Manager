import os

from loader.utils import generate_storage_patch
from loader.utils import create_compilation

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UCA_Manager.settings")
import django
django.setup()

from django.test import SimpleTestCase
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
from django.conf import settings
from loader.utils import Utils
from loader.models import PostEntry, Compilation
from UCA_Manager.settings import PATH_TO_STORE

from loader.tumblr_loader import TumblrLoader

# import sys
# sys.path.append("../")

# from postCalendar.models import Calendar
# from account.models import Account
# import loader.models


class Test_TumblrLoader(SimpleTestCase):

    # @pytest.fixture
    # TODO: make the function fixture
    def prepare_db(self):
        # settings.configure()

        Utils.start_session()

        sync_table(PostEntry)
        sync_table(Compilation)

        drop_table(PostEntry)
        drop_table(Compilation)

    # TODO: make the function fixture
    def create_parser(self):
        return TumblrLoader()

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
        path = generate_storage_patch(PATH_TO_STORE, tags=tag)


        # tmblr.download(number, tag=tag)

        blogs = ['netmassimo', 'kinogane']

        compilation = create_compilation(
            resource='Tumbler',
            name='Test',
            tag=tag,
            blogs=blogs,
            storage=path
        )
        tmblr.download(compilation, number, storagePath=path, blogs=blogs)


        pe = PostEntry.objects.all()
        pe = sorted(pe, key=lambda post: post['posted_timestamp'], reverse=True)


        print("PostEntryes:")
        for instance in pe:
            print(f"<===== ===== ===== instance.id: {instance.id} ===== ===== =====>")

            # print(f"instance.blog_name: {instance.blog_name}")
            # print(f"instance.blog_url: {instance.blog_url}")
            # print(f"instance.id_in_social_network: {instance.id_in_social_network}")
            print(f"instance.url: {instance.url}")
            # print(f"instance.posted_date: {instance.posted_date}")
            # print(f"instance.post_tags: {instance.post_tags}")
            # print(f"instance.text: {instance.text}")
            print(f"instance.file_urls: {instance.file_urls}")
            print(f"instance.external_link_urls: {instance.external_link_urls}")

            # print(f"instance.tags: {instance.tags}")

            print(f"instance.file_urls: {instance.stored_file_urls}")
            # print(f"instance.external_link_urls: {instance.external_link_urls}")
            #
            # print(f"instance.description: {instance.description}")



            # print(f"<===== ===== =====  * * * * *  ===== ===== =====>\n")
            # print("\n")

        print("\nCompilation:")
        comps = Compilation.objects.all()
        for comp in comps:
            print(f"comp.id {comp.id}")
            print(f"comp.resource {comp.resource}")
            print(f"comp.search_tag {comp.search_tag}")
            print(f"comp.search_blogs {comp.search_blogs}")
            print(f"comp.update_date {comp.update_date}")
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

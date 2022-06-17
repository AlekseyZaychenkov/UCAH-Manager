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


from loader.vk_loader import VKLoader

# import sys
# sys.path.append("../")

# from workspace_editor.models import Schedule
# from account.models import Account
# import loader.models


class Test_VKLoader(SimpleTestCase):

    # @pytest.fixture
    # TODO: make the function fixture
    def prepare_db(self):
        # settings.configure()

        Utils.start_session()

        sync_table(PostEntry)
        sync_table(Compilation)

        # drop_table(PostEntry)
        # drop_table(Compilation)

    # TODO: make the function fixture
    def create_loader(self):
        return VKLoader()

    # TODO: test method for generate_storage_patch()
    # TODO: test method for save_files()



    def print_user_info(self, client):
        userInfo = (client.info())['user']
        print(f"My user for connection to Tumbler:"
              f"\nname: {userInfo['name']}"
              f"\nfollowing: {userInfo['following']}"
              f"\ndefault_post_format: {userInfo['default_post_format']}"
              f"\nlikes: {userInfo['likes']}"
              f"\nblogs: {len(userInfo['blogs'])}"
              )


    def test_upload(self):
        self.prepare_db()

        vk = self.create_loader()

        posts = PostEntry.objects.all()
        posts = sorted(posts, key=lambda post: post['posted_timestamp'], reverse=True)

        print("PostEntryes:")
        for post in posts:
            # print(f"post: {post}")

            # print(f"<===== ===== ===== post.id: {post.id} ===== ===== =====>")
            #
            # print(f"post.blog_name: {post.blog_name}")
            # print(f"post.url: {post.url}")
            #
            # print(f"post.tags: {post.tags}")
            # print(f"post.text: {post.text}")
            #
            # print(f"post.external_link_urls: {post.external_link_urls}")
            # print(f"post.file_urls: {post.stored_file_urls}")
            #
            # print(f"<===== ===== =====  * * * * *  ===== ===== =====>\n")
            # print("\n")

            if len(post.stored_file_urls) > 0:
                vk.upload(post)
                break








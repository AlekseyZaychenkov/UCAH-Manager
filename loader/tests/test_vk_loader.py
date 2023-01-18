import os

from credentials import VK_APP_TOKEN

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UCA_Manager.settings")
import django
django.setup()

from django.test import SimpleTestCase
from cassandra.cqlengine.management import sync_table
from loader.utils import Utils
from loader.models import Post, Compilation

from loader.vk_loader import VKLoader


class Test_VKLoader(SimpleTestCase):

    # @pytest.fixture
    # TODO: make the function fixture
    def prepare_db(self):
        # settings.configure()

        Utils.start_session()

        sync_table(Post)
        sync_table(Compilation)

        # drop_table(Post)
        # drop_table(Compilation)

    # TODO: make the function fixture
    def create_loader(self):
        return VKLoader(vk_app_token=VK_APP_TOKEN)

    # TODO: test method for generate_storage_path()
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

        # TODO: actualise from posts to events

        # vk = self.create_loader()

        # posts = Post.objects.all()
        # posts = sorted(posts, key=lambda post: post['posted_timestamp'], reverse=True)
        #
        # print("Events:")
        # for post in posts:
        #     print(f"Started uploading post {post.id}")
        #     vk.upload(post)



    def test_get_controlled_blogs(self):
        self.prepare_db()

        vk = self.create_loader()

        blogs = vk.get_controlled_blogs_resource_numbers()
        print("Available blogs VKontakte:")
        print(blogs)


    def test_get_blog_info(self):
        self.prepare_db()

        vk = self.create_loader()

        blogs = vk.get_controlled_blogs_resource_numbers()

        info = vk.get_blogs_info(blogs_list = blogs['items'])
        print("Blog VKontakte info:")
        print(info)








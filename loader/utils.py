import os
from datetime import datetime

from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
import pytumblr as pytumblr
import vk
import urllib


from loader.models import Compilation, PostEntry, ExampleModel
from credentials import TUMBLR_OATH_SECRET, TUMBLR_CONSUMER_SECRET, TUMBLR_CONSUMER_KEY, TUMBLR_OATH_TOKEN, VK_APP_ID, \
    VK_USER_LOGIN, VK_USER_PASSWORD, VK_UCA_GROUP_TOKEN, VK_AUTHORIZATION_CODE

# import sys
# sys.path.append("../../loader")
from account.settings import IS_TEST, CASSANDRA_DB_ADRESSES, TEST_CASSANDRA_KEYSPACE_NAME, CASSANDRA_KEYSPACE_NAME


# TODO: delete Utils and make all methods with import from loader.utils import method_name
from UCA_Manager.settings import ROOT_DIR


class Utils:

    @staticmethod
    def start_session():
        if IS_TEST:
            connection.setup(CASSANDRA_DB_ADRESSES.split(","), TEST_CASSANDRA_KEYSPACE_NAME, protocol_version=3)
        else:
            connection.setup(CASSANDRA_DB_ADRESSES.split(","), CASSANDRA_KEYSPACE_NAME, protocol_version=3)


    @staticmethod
    def sync_models():
        sync_table(ExampleModel)
        sync_table(PostEntry)
        sync_table(Compilation)


    @staticmethod
    def drop_models():
        drop_table(ExampleModel)
        drop_table(PostEntry)
        drop_table(Compilation)


    @staticmethod
    def create_tumblr_client():
        return pytumblr.TumblrRestClient(
            TUMBLR_CONSUMER_KEY,
            TUMBLR_CONSUMER_SECRET,
            TUMBLR_OATH_TOKEN,
            TUMBLR_OATH_SECRET
        )

    @staticmethod
    def create_vk_client():
        # session = vk_api.VkApi(VK_APP_ID, VK_USER_LOGIN, VK_USER_PASSWORD)
        session = vk_api.VkApi(VK_USER_LOGIN, VK_USER_PASSWORD)
        session.auth()
        return session



    # @staticmethod
    # def create_vk_session():
    #     session = vk.VkApi(VK_APP_ID, VK_USER_LOGIN, VK_USER_PASSWORD)
    #     session.auth()
    #     return session


# TODO: rename storage to storage_path
def create_compilation(resource, name=None, tag=None, blogs=None, storage=None):
    return Compilation.create(
        name            = name,
        resource        = resource,
        search_tag      = tag,
        search_blogs    = blogs,
        update_date     = str(datetime.now()),
        storage         = storage,
        post_ids        = list()
    )


def generate_storage_patch(root_path, comp_id=None, others=None):
    path = root_path
    if comp_id:
        path = os.path.join(path, str(comp_id))
    if others:
        path = os.path.join(path, others)
    return path



def create_tumblr_client():
    return pytumblr.TumblrRestClient(
        TUMBLR_CONSUMER_KEY,
        TUMBLR_CONSUMER_SECRET,
        TUMBLR_OATH_TOKEN,
        TUMBLR_OATH_SECRET
    )

    # @staticmethod
    # def create_vk_client():
    #     pass
    #     # return pytumblr.TumblrRestClient(
    #     #     CONSUMER_KEY,
    #     #     CONSUMER_SECRET,
    #     #     OATH_TOKEN,
    #     #     OATH_SECRET
    #     # )

def two_factor():
    code = input('Enter Two-factor Auth code: ')
    remember_device = True
    return code, remember_device



def create_vk_session():
    # session = vk_api.VkApi(app_id=VK_APP_ID ,
    #                        login=VK_USER_LOGIN,
    #                        password=VK_USER_PASSWORD,
    #                        token=VK_AUTHORIZATION_CODE
    #                        )
    PERMISSIONS = 'friends,photos,messages,wall,offline,docs,groups,stats'

    session = vk_api.VkApi(VK_USER_LOGIN, VK_USER_PASSWORD,
                 auth_handler=two_factor,
                 app_id=VK_APP_ID,
                 scope=PERMISSIONS,
                 config_filename='vk_config.v2.json')
    session.auth()
    print(f"session: {session}")
    # session.auth()
    return session


# TODO: rename storage to storage_path
def create_compilation(resource, name=None, tag=None, blogs=None, storage=None):
    return Compilation.create(
        name            = name,
        resource        = resource,
        search_tag      = tag,
        search_blogs    = blogs,
        update_date     = str(datetime.now()),
        storage         = storage,
        post_ids        = list()
    )


def generate_storage_patch(root_path, comp_id=None, others=None):
    path = root_path
    if comp_id:
        path = os.path.join(path, str(comp_id))
    if others:
        path = os.path.join(path, others)
    return path


# TODO: rename storage to storage_path
def create_compilation(resource, name=None, tag=None, blogs=None, storage=None):
    return Compilation.create(
        name            = name,
        resource        = resource,
        search_tag      = tag,
        search_blogs    = blogs,
        update_date     = str(datetime.now()),
        storage         = storage,
        post_ids        = list()
    )


def generate_storage_patch(root_path, comp_id=None, others=None):
    path = root_path
    if comp_id:
        path = os.path.join(path, str(comp_id))
    if others:
        path = os.path.join(path, others)
    return path


def save_files(storagePath, file_urls):
    if storagePath is not None:
        print(f"Trying to create directory '{storagePath}'")
        os.makedirs(storagePath, exist_ok=True)

    # TODO: implement realization for cloud (google-drive) storing
    savedFileAddresses = list()

    print(f"Downloading and saving files (images and gifs) to '{storagePath}'")
    for image_url in file_urls:
        path_to_image = os.path.join(storagePath, os.path.basename(image_url))

        opener = urllib.request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0')
        filename, headers = opener.retrieve(image_url, path_to_image)
        relative_path = os.path.relpath(filename, ROOT_DIR)

        savedFileAddresses.append(relative_path)

    return savedFileAddresses

import os
from datetime import datetime

from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
import pytumblr as pytumblr
import vk
import urllib


from loader.models import Compilation, Post
from credentials import TUMBLR_OATH_SECRET, TUMBLR_CONSUMER_SECRET, TUMBLR_CONSUMER_KEY, TUMBLR_OATH_TOKEN

from account.settings import IS_TEST, CASSANDRA_DB_ADRESSES, TEST_CASSANDRA_KEYSPACE_NAME, CASSANDRA_KEYSPACE_NAME, \
    PATH_TO_STORE

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
        sync_table(Post)
        sync_table(Compilation)


    @staticmethod
    def drop_models():
        drop_table(Post)
        drop_table(Compilation)


    @staticmethod
    def create_tumblr_client():
        return pytumblr.TumblrRestClient(
            TUMBLR_CONSUMER_KEY,
            TUMBLR_CONSUMER_SECRET,
            TUMBLR_OATH_TOKEN,
            TUMBLR_OATH_SECRET
        )


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


def create_empty_compilation():
    path = generate_storage_patch(PATH_TO_STORE, others='autocreated')
    return create_compilation(resource='Created by utils', tag=None, blogs=None, storage=path)


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


def create_vk_client(token):
    session = vk.Session(access_token=token)
    return vk.API(session)


def two_factor():
    code = input('Enter Two-factor Auth code: ')
    remember_device = True
    return code, remember_device


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


def save_files(storage_path, file_urls):
    if storage_path is not None:
        print(f"Trying to create directory '{storage_path}'")
        os.makedirs(storage_path, exist_ok=True)

    # TODO: implement realization for cloud (google-drive) storing
    savedFileAddresses = list()

    print(f"Downloading and saving files to '{storage_path}'")
    for image_url in file_urls:
        path_to_image = os.path.join(storage_path, os.path.basename(image_url))

        opener = urllib.request.URLopener()
        opener.addheader('User-Agent', 'Mozilla/5.0')
        filename, headers = opener.retrieve(image_url, path_to_image)
        relative_path = os.path.relpath(filename, ROOT_DIR)

        savedFileAddresses.append(relative_path)

    return savedFileAddresses


def save_files_from_request(storage_path, uploaded_in_memory_files):
    if storage_path is not None:
        print(f"Trying to create directory '{storage_path}'")
    os.makedirs(storage_path, exist_ok=True)

    # TODO: implement realization for cloud (google-drive) storing
    saved_file_addresses = list()

    print(f"Downloading and saving files to '{storage_path}'")
    for file in uploaded_in_memory_files:
        path_to_image = os.path.join(storage_path, os.path.basename(file.name))
        with open(path_to_image, 'wb') as destination:
            b = file.file
            destination.write(b.read())
            saved_file_addresses.append(path_to_image)

    return saved_file_addresses


def delete_dir(dir_to_search):
    success = True
    for dirpath, dirnames, filenames in os.walk(dir_to_search):
        try:
            os.rmdir(dirpath)
        except OSError as ex:
            print(ex)
            success = False
    return success

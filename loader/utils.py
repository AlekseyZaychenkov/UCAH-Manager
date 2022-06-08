import os
from datetime import datetime

from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
import pytumblr as pytumblr
import urllib

from loader.models import Compilation, PostEntry, ExampleModel
from credentials import OATH_SECRET, CONSUMER_SECRET, CONSUMER_KEY, OATH_TOKEN

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
    def createTumblrClient():
        return pytumblr.TumblrRestClient(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            OATH_TOKEN,
            OATH_SECRET
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


def generate_storage_patch(root_path, tags=None, blogs=None, others=None):
    b = '_'.join(blogs) if blogs else ""
    if isinstance(tags, str):
        t = tags
    if isinstance(tags, list):
        t = '_'.join(tags)
    if tags == None:
        t = ''

    # TODO: set instead of datatime name of compilation
    return os.path.join(root_path, f"tags--{t}-blogs--{b}-others-{others}--datetime--{datetime.now()}")


    @staticmethod
    def createTumblrClient():
        return pytumblr.TumblrRestClient(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            OATH_TOKEN,
            OATH_SECRET
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


def generate_storage_patch(root_path, tags=None, blogs=None, others=None):
    b = '_'.join(blogs) if blogs else ""
    if isinstance(tags, str):
        t = tags
    if isinstance(tags, list):
        t = '_'.join(tags)
    if tags == None:
        t = ''
    return os.path.join(root_path, f"tags--{t}-blogs--{b}-others-{others}--datetime--{datetime.now()}")


    @staticmethod
    def createTumblrClient():
        return pytumblr.TumblrRestClient(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            OATH_TOKEN,
            OATH_SECRET
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


def generate_storage_patch(root_path, tags=None, blogs=None, others=None):
    b = '_'.join(blogs) if blogs else ""
    if isinstance(tags, str):
        t = tags
    if isinstance(tags, list):
        t = '_'.join(tags)
    if tags == None:
        t = ''
    return os.path.join(root_path, f"tags--{t}-blogs--{b}-others-{others}--datetime--{datetime.now()}")


def save_files(storagePath, file_urls):
    if storagePath is not None:
        print(f"Trying to create directory '{storagePath}'")
        os.makedirs(storagePath)

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
import os
import uuid
import pytumblr as pytumblr
import urllib.request
from bs4 import BeautifulSoup


from cassandra.cqlengine.management import sync_table
from models import PostEntry
from datetime import datetime



class TumblrLoader:

    def __init__(self, consumer_key, consumer_secret, oath_token, oath_secret):
        self.client = pytumblr.TumblrRestClient(
            consumer_key,
            consumer_secret,
            oath_token,
            oath_secret,
        )
        sync_table(PostEntry)


    def save_files(self, storagePach, file_urls):
        # TODO: implement realization for cloud (google-drive) storing
        savedFileAddresses = list()

        print(f"Downloading and saving files (images and gifs) to '{storagePach}'")
        for image_url in file_urls:
            path_to_image = os.path.join(storagePach, os.path.basename(image_url))

            opener = urllib.request.URLopener()
            opener.addheader('User-Agent', 'Mozilla/5.0')
            filename, headers = opener.retrieve(image_url, path_to_image)

            savedFileAddresses.append(path_to_image)

        return savedFileAddresses

    # TODO: implement bool flag 'storeFilesLocal' (for downloading images and gifs or not)
    def save(self, response, compilation_id, storagePath, tag=''):
        print(f"Start parsing response:")
        for post in response:
            postId = post['id']

            print(f"\npost['blog']['name']: {post['blog']['name']}"
                  f"\npostId: {postId}"
                  f"\npost['post_url']: {post['post_url']}\n\n")

            file_urls = list()
            external_urls = list()
            description = str()

            if post['type'] == 'video' and 'permalink_url' in post:
                description += f"original's post 'type' is 'video'"
                # TODO: check how it works with multiple videos, if it possible
                external_urls.append(post['permalink_url'])

            if('body' in post):
                body = post['body']
                # print(f"Flag 00 body: {body}\n")
                soup = BeautifulSoup(body, 'html.parser')

                for link in soup.find_all('img'):
                    file_urls.append(link.get('src'))

                for link in soup.find_all('a'):
                    external_urls.append(link.get('href'))

                # TODO: check if it works or not
                # TODO: check for post with gifs
                # for link in soup.find_all():
                #     print(f"data-url: {link.get('data-url')}\n")

            if('photos' in post):
                for p in post['photos']:
                    file_urls.append(p['original_size']['url'])


            # TODO: implement method for saving images from urls to local or cloud storage
            # TODO: use enam for choising type of storage
            # TODO: figure is possible use mock for tests calling self.save_files() or not
            savedFileAddresses = self.save_files(storagePath, file_urls) if storagePath is not None else None


            PostEntry.create(
                # information about original post
                original_resource            = 'Tumbler',
                original_blog_name           = post['blog']['name'],
                original_blog_url            = post['blog']['url'],
                original_post_id             = postId,
                original_post_url            = post['post_url'],
                original_posted_date         = post['date'],
                original_posted_timestamp    = post['timestamp'],
                original_post_tags           = post['tags'],
                original_text                = post['body'] if 'body' in post else "",
                original_file_urls           = file_urls,
                original_external_link_urls  = external_urls,

                # information about search query parameters
                search_tag                   = tag,
                downloated_date              = str(datetime.now()),
                compilation_id               = compilation_id,

                # information for posting
                text                         = post['body'] if 'body' in post else "",
                file_urls                    = savedFileAddresses,
                external_link_urls           = external_urls,

                # information for administration notes and file storing
                description                  = description,
                storage                      = storagePath
            )


    def download(self, number, storagePath=None, tag=None, blogs=None):
        print(f"Getting '{number}' posts from Tambler by tag: '{tag}' and blogs '{blogs}'")
        if storagePath is not None:
            print(f"Trying to create directory '{storagePath}'")
            os.makedirs(storagePath)

        look_before = 0
        compilation_id = uuid.uuid1()
        response = list()

        if blogs == None:
            while number > 0:
                limit = 20 if number > 20 else number

                # TODO: gathering: keep posts with one of specific tags (relationship 'OR')
                response = self.client.tagged(tag=tag, limit=limit, before=look_before)

                # TODO: filter out: keep posts with a specific tag
                # TODO: filter out: gathering only posts with several tags together (relationship 'AND')
                # TODO: sort posts by timestamp and filter out posts beyond requested number

                print(f"Downloaded '{len(response)}' posts with tag '{tag}' from Tumblr")
                self.save(response, compilation_id, storagePath=storagePath, tag=tag)

                look_before = response[-1]['timestamp']
                number -= len(response)
                print(f"look_before timestamp: {look_before}\n")

        else:
            limit = 10 if number > 10 else number
            # TODO: gathering: keep posts with one of specific tags (relationship 'OR')
            for blog in blogs:
                # TODO: check if it works
                r = self.client.posts(blog, limit=limit, before=look_before, reblog_info=True, notes_info=True)\
                    if tag is None \
                    else \
                    self.client.posts(blog, tag=tag, limit=limit, before=look_before, reblog_info=True, notes_info=True)

                response.extend(r['posts'])

            # TODO: filter out: keep posts with a specific tag
            # TODO: filter out: gathering only posts with several tags together (relationship 'AND')
            # TODO: sort posts by timestamp and filter out posts beyond requested number

            response = sorted(response, key=lambda post: post['timestamp'], reverse=True)
            response = response[0:number]

            print(f"Downloaded '{len(response)}' posts from Tumblr")


            self.save(response, compilation_id, storagePath=storagePath, tag=tag)

            look_before = response[-1]['timestamp']
            number -= len(response)


    def generate_storage_patch(self, root_path, tags, blogs=None):
        blogs = f"-blogs--{'_'.join(blogs)}" if blogs else ""
        return os.path.join(root_path, f"tags--{'_'.join(tags)}{blogs}-datetime--{datetime.now()}")

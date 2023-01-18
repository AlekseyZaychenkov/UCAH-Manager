import os
from bs4 import BeautifulSoup


from cassandra.cqlengine.management import sync_table
from loader.models import Post, Compilation
from loader.utils import Utils, save_files_from_urls, create_tumblr_client

import pathlib


class TumblrLoader:

    def __init__(self):
        self.client = create_tumblr_client()
        sync_table(Post)
        sync_table(Compilation)

    def print_user_info(self):
        user_info = (self.client.info())['user']
        print(f"My user for connection to Tumbler:"
              f"\nname: {user_info['name']}"
              f"\nfollowing: {user_info['following']}"
              f"\ndefault_post_format: {user_info['default_post_format']}"
              f"\nlikes: {user_info['likes']}"
              f"\nblogs: {len(user_info['blogs'])}"
              )


    # TODO: implement bool flag 'storeFilesLocal' (for downloading images and gifs or not)
    def save(self, response, compilation, storage_path=None, tag=''):
        old_post_ids = compilation.post_ids
        social_network_post_ids = []
        for old_post_id in old_post_ids:
            post = Post.objects.get(id=old_post_id)
            social_network_post_ids.append(post.id_in_social_network)

        print(f"Start parsing response:")
        for post in response:
            post_id = post['id']

            if post_id in social_network_post_ids:
                continue
            # if post_id != 681406879305498624:
            #     continue

            print(f"\npost['blog']['name']: {post['blog']['name']}"
                  f"\npost_id: {post_id}"
                  f"\npost['post_url']: {post['post_url']}\n\n")
            # print(f"\nPost: {post}")

            file_urls = list()
            external_urls = list()
            description = str()

            description += f"original post has type '{post['type']}'"
            if post['type'] == 'video' and 'permalink_url' in post:
                # TODO: check how it works with multiple videos, if it possible
                external_urls.append(post['permalink_url'])

            if 'description' in post:
                soup = BeautifulSoup(post['description'], 'html.parser')
                for link in soup.find_all('img'):
                    file_urls.append(link.get('src'))

            if 'body' in post:
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

            if'photos' in post:
                for p in post['photos']:
                    file_urls.append(p['original_size']['url'])


            # TODO: implement method for saving images from urls to local or cloud storage
            # TODO: use enum to select type of storage
            # TODO: figure is possible use mock for tests calling self.save_files() or not

            post_storage_path = os.path.join(storage_path, str(post_id))
            saved_file_addresses = save_files_from_urls(post_storage_path, file_urls=file_urls) if len(file_urls) > 0 else None

            post = Post.create(
                # information about original post
                blog_name             = post['blog']['name'],
                blog_url              = post['blog']['url'],
                id_in_social_network  = post_id,
                original_post_url     = post['post_url'],
                posted_date           = post['date'],
                posted_timestamp      = post['timestamp'],
                tags                  = post['tags'],
                text                  = post['body'] if 'body' in post else "",
                file_urls             = file_urls,

                # information about search query parameters
                compilation_id        = compilation.id,

                # information for posting
                stored_file_urls      = saved_file_addresses,
                external_link_urls    = external_urls,

                # information for administration notes and file storing
                description           = description
            )

            if compilation.post_ids is None:
                compilation.post_ids = [post.id]
            else:
                compilation.post_ids.append(post.id)

            compilation.update()


    # TODO: add time limit
    def download(self, compilation, number, storage_path=None, tag=None, blogs=None):
        print(f"Getting '{number}' posts from Tumbler by tag: '{tag}' and blogs '{blogs}'")

        look_before = 0
        response = list()

        if blogs is None:
            while number > 0:
                limit = 20 if number > 20 else number

                # TODO: gathering: keep posts with one of specific tags (relationship 'OR')
                response = self.client.tagged(tag=tag, limit=limit, before=look_before)

                # TODO: filter out: keep posts with a specific tag
                # TODO: filter out: gathering only posts with several tags together (relationship 'AND')
                # TODO: sort posts by timestamp and filter out posts beyond requested number

                print(f"Downloaded '{len(response)}' posts with tag '{tag}' from Tumblr")
                self.save(response, compilation, storage_path=storage_path, tag=tag)

                if len(response) == 0:
                    break

                look_before = response[-1]['timestamp']
                number -= len(response)
                print(f"look_before timestamp: {look_before}\n")

        else:
            while number > 0:
                limit = 10 if number > 10 else number
                # TODO: gathering: keep posts with one of specific tags (relationship 'OR')
                for blog in blogs:
                    # TODO: check if it works
                    r = self.client.posts(blog, limit=limit, before=look_before, reblog_info=True, notes_info=True)\
                        if tag is None \
                        else \
                        self.client.posts(blog, tag=tag, limit=limit, before=look_before, reblog_info=True, notes_info=True)
                    response.extend(r['posts'])

                if len(response) == 0:
                    break

                # TODO: filter out: keep posts with a specific tag
                # TODO: filter out: black list of blogs
                # TODO: filter out: gathering only posts with several tags together (relationship 'AND')
                # TODO: sort posts by timestamp and filter out posts beyond requested number

                response = sorted(response, key=lambda post: post['timestamp'], reverse=True)
                response = response[0:number]

                print(f"Downloaded '{len(response)}' posts from Tumblr")


                self.save(response, compilation, storage_path=storage_path, tag=tag)

                look_before = response[-1]['timestamp']
                number -= len(response)

import datetime
import json
import os
import logging
from time import sleep
import requests
import vk
from UCA_Manager.settings import PATH_TO_STORE, MEDIA_ROOT

from cassandra.cqlengine.management import sync_table

from credentials import VK_UCA_GROUP_NUMBER, VK_USER_ID, VK_APP_TOKEN,  VK_API_VERSION
from loader.models import Post, Compilation
from workspace_editor.models import Event
from loader.utils import create_vk_client


log = logging.getLogger(__name__)


class VKLoader:

    def __init__(self, vk_app_token):
        sync_table(Post)
        sync_table(Compilation)
        self.vk_app_token = vk_app_token
        self.vk_client = create_vk_client(vk_app_token)
        vk.logger.setLevel('DEBUG')


    def get_controlled_blogs_resource_numbers(self):
        blogs_list = list()

        retry_after = 1
        delay = True
        while delay:
            delay = False
            try:
                log.debug(f"[{self.__make_time()}] Downloading list of blogs from vk...")

                blogs_list= self.vk_client.groups.get(
                                         filter=['admin', 'editor'],
                                         v=VK_API_VERSION)

                log.debug(f"List of blogs successfully downloaded.")

            except vk.exceptions.VkAPIError as err:
                log.warning(f"[{self.__make_time()}] - Error {err}")
                if int(err.code) == 6:
                    delay = True
                    sleep(retry_after)
                    log.debug(f"[{self.__make_time()}] sleep {retry_after} sec")

            except Exception as err:
                log.error(f"[{self.__make_time()}] - Error {err}")

        return blogs_list


    def get_blogs_info(self, blogs_list:list):
        blogs_info_list = dict()

        retry_after = 1
        delay = True
        while delay:
            delay = False
            try:
                log.info(f"[{self.__make_time()}] !!! Downloading info for blogs with ids='{blogs_list['items']}' ...")

                blogs_info = self.vk_client.groups.getById(access_token=self.vk_app_token,
                                                              group_ids=blogs_list["items"],
                                                              v=VK_API_VERSION)

                for blog_info in blogs_info:
                    blogs_info_list[blog_info["name"]] = BlogInfo(name = blog_info["name"],
                                                               avatar_url = blog_info["photo_200"],
                                                               blog_resource_number = blog_info["id"],
                                                               url = f'vk.com/{blog_info["screen_name"]}')

                log.info(f"Dict of blogs successfully downloaded.")
                log.info(f"Blog info: {blogs_info.values()}")
            except vk.exceptions.VkAPIError as err:
                log.warning(f"[{self.__make_time()}] - Error {err}")
                if int(err.code) == 6:
                    delay = True
                    sleep(retry_after)
                    log.debug(f"[{self.__make_time()}] sleep {retry_after} sec")

            except Exception as err:
                log.error(f"[{self.__make_time()}] - Error {err}")

        return blogs_info_list


    def upload(self, event: Event, as_soon_as_possible=False):
        if Post.objects.filter(id=event.post_id).count() == 0:
            logging.error(f"For event with id='{event.event_id}' "
                          f"post with id='{event.post_id}' was haven't found in cassandra")
            return
        else:
            post = Post.objects.get(id=event.post_id)

        tags_str = self.__prepate_tags_string(post.tags)

        message = ''
        message += tags_str
        message += '\n'
        message += post.text

        retry_after = 1
        delay = True
        while delay:
            delay = False
            try:
                log.debug(f"[{self.__make_time()}] Uploading files to server vk...")
                attachments = self.__prepare_attachments(post.stored_file_urls)
                publish_date = self.__convert_publish_data(event.datetime)

                log.debug(f"[{self.__make_time()}] Posting...'.")
                self.vk_client.wall.post(access_token=self.vk_app_token,
                                         owner_id=-VK_UCA_GROUP_NUMBER,
                                         message=message,
                                         attachments=attachments,
                                         publish_date=publish_date,
                                         copyright = post.original_post_url,
                                         v=VK_API_VERSION)

                log.info(f"[{self.__make_time()}] post {post.id} successfully uploaded.")

            except vk.exceptions.VkAPIError as err:
                log.warning(f"[{self.__make_time()}] - Error {err}")
                if int(err.code) == 6:
                    delay = True
                    sleep(retry_after)
                    log.debug(f"[{self.__make_time()}] sleep {retry_after} sec")

            except Exception as err:
                log.error(f"[{self.__make_time()}] - Error {err}")


    def __make_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")


    def __prepare_attachments(self, stored_file_urls):
        if stored_file_urls is None:
            return None

        paths = []
        for path in stored_file_urls:
            paths.append(str(os.path.join('..', MEDIA_ROOT, path)))

        if len(paths) > 10:
            log.warning('Created post has more then 10 attachments! VK only allows 10 attachments per 1 post!')
            paths = paths[:10]

        attachments = []
        img_upload_url = None
        doc_upload_url = None

        # TODO: consider multiple uploading files or images per one request
        for path in paths:
            if path.endswith('.jpg') or path.endswith('.png') or path.endswith('.jpeg'):
                if not img_upload_url:
                    img_upload_url = self.__get_img_upload_url()

                # путь к изображению
                file = {'photo': (path, open(path, 'rb'))}

                # Загружаем изображение на url
                response = requests.post(img_upload_url, files=file)
                result = json.loads(response.text)

                # Сохраняем фото на сервере и получаем id
                data = self.vk_client.photos.saveWallPhoto(server=int(result['server']),
                                                           photo=result['photo'],
                                                           hash=result['hash'],
                                                           v=VK_API_VERSION
                                                           )

                attachments.append(f"photo{VK_USER_ID}_{data[0]['id']}")

            elif path.endswith('.gif') or path.endswith('.giff') or path.endswith('.txt'):
                if not doc_upload_url:
                    doc_upload_url = self.__get_doc_upload_url()

                # путь к документу
                file = {'file': (path, open(path, 'rb'))}

                # Загружаем документ на url
                response = requests.post(doc_upload_url, files=file)
                result = json.loads(response.text)

                # Сохраняем документ на сервере и получаем id
                data = self.vk_client.docs.save(file=result['file'],
                                                v=VK_API_VERSION
                                                )

                attachments.append(f"doc{data['doc']['owner_id']}_{data['doc']['id']}")

        return attachments


    def __convert_publish_data(self, event_time):
        return event_time.timestamp()


    def __get_img_upload_url(self):
        # Получаем ссылку для загрузки изображений
        method_url = 'https://api.vk.com/method/photos.getWallUploadServer?'
        response = requests.post(method_url,
                                 dict(access_token=self.vk_app_token,
                                      gid=VK_UCA_GROUP_NUMBER,
                                      v=VK_API_VERSION)
                                 )
        result = json.loads(response.text)
        return result['response']['upload_url']


    def __get_doc_upload_url(self):
        method_url = 'https://api.vk.com/method/docs.getWallUploadServer?'
        response = requests.post(method_url,
                                 dict(access_token=self.vk_app_token,
                                      gid=VK_UCA_GROUP_NUMBER,
                                      v=VK_API_VERSION)
                                 )
        result = json.loads(response.text)
        return result['response']['upload_url']


    def __remove_stored_docs(self, attachments):
        for a in attachments:
            if a.startswith('doc'):
                ids = a[3:]
                owner_id = ids.split('_')[0]
                doc_id = ids.split('_')[1]
                self.vk_client.docs.delete(owner_id=owner_id,
                                           doc_id=doc_id,
                                           v=VK_API_VERSION
                                           )


    def __prepate_tags_string(self, post_tags):
        if post_tags is None:
            return None

        tags = []
        # TODO: implement limit of not more than 10 tags
        for tag in post_tags:
            tag = tag.strip()
            tag = tag.replace(' ', '_')
            tag = tag.replace('-', '_')
            tag = tag.replace('+', '')
            tag = '#' + tag
            tags.append(tag)

        return " ".join(tags)


class BlogInfo:
    name:str
    avatar_url:str
    blog_resource_number:int
    url:str
    added:bool
    id:int

    def __init__(self, name:str, avatar_url:str, blog_resource_number:int, url:str):
        self.name = name
        self.avatar_url = avatar_url
        self.blog_resource_number = blog_resource_number
        self.url = url




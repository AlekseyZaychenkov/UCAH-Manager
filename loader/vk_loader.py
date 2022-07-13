import datetime
import json
import os
import logging
from time import sleep
import requests
import vk

from cassandra.cqlengine.management import sync_table

from credentials import VK_UCA_GROUP_NUMBER, VK_USER_ID, VK_APP_TOKEN,  VK_API_VERSION
from loader.models import PostEntry, Compilation
from utils import create_vk_client


logger = logging.getLogger(__name__)


class VKLoader:

    def __init__(self):
        sync_table(PostEntry)
        sync_table(Compilation)
        self.vk_client = create_vk_client(VK_APP_TOKEN)
        vk.logger.setLevel('DEBUG')


    def upload(self, post):

        tags_str = self.__prepate_tags_string(post.tags)

        message = ''
        message += tags_str
        message += '\n'
        message += post.text

        retry_after = 1
        delay = True
        while (delay):
            delay = False
            try:
                logger.debug(f"[{self.__make_time()}] Uploading files to server vk...")
                attachments = self.__prepare_attachments(post.stored_file_urls)

                logger.debug(f"[{self.__make_time()}] Posting...'.")
                self.vk_client.wall.post(access_token=VK_APP_TOKEN,
                                         owner_id=-VK_UCA_GROUP_NUMBER,
                                         message=message,
                                         attachments=attachments,
                                         copyright = post.original_post_url,
                                         v=VK_API_VERSION
                                         )

                logger.info(f"[{self.__make_time()}] post {post.id} successfully uploaded.")

            except vk.exceptions.VkAPIError as err:
                logger.warning(f"[{self.__make_time()}] - Error {err}")
                if int(err.code) == 6:
                    delay = True
                    sleep(retry_after)
                    logger.debug(f"[{self.__make_time()}] sleep {retry_after} sec")

            except Exception as err:
                logger.error(f"[{self.__make_time()}] - Error {err}")


    def __make_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")


    def __prepare_attachments(self, stored_file_urls):
        if stored_file_urls is None:
            return None

        paths = []
        for path in stored_file_urls:
            paths.append(str(os.path.join('..', path)))

        if len(paths) > 10:
            logger.warning('Created post has more then 10 attachments! VK only allows 10 attachments per 1 post!')
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


    def __get_img_upload_url(self):
        # Получаем ссылку для загрузки изображений
        method_url = 'https://api.vk.com/method/photos.getWallUploadServer?'
        response = requests.post(method_url,
                                 dict(access_token=VK_APP_TOKEN,
                                      gid=VK_UCA_GROUP_NUMBER,
                                      v=VK_API_VERSION)
                                 )
        result = json.loads(response.text)
        return result['response']['upload_url']


    def __get_doc_upload_url(self):
        method_url = 'https://api.vk.com/method/docs.getWallUploadServer?'
        response = requests.post(method_url,
                                 dict(access_token=VK_APP_TOKEN,
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
        for tag in post_tags:
            tag = tag.strip()
            tag = tag.replace(' ', '_')
            tag = tag.replace('-', '_')
            tag = tag.replace('+', '')
            tag = '#' + tag
            tags.append(tag)

        return " ".join(tags)

import json
import os
import logging



import vk
from cassandra.cqlengine.management import sync_table

from credentials import VK_UCA_GROUP_TOKEN, VK_USER_LOGIN, VK_USER_PASSWORD, VK_UCA_GROUP_NUMBER, VK_USER_ID, \
    VK_APP_TOKEN, VK_APP_ID, VK_API_VERSION, VK_USER_TOKEN, VK_APP_PASSWORD
from loader.models import PostEntry, Compilation

import requests
logger = logging.getLogger(__name__)


class VKLoader:

    def __init__(self):
        # self.client = Utils.create_vk_client()
        # self.session = create_vk_session()
        sync_table(PostEntry)
        sync_table(Compilation)


    def upload(self, post):
        # vk_session = self.session
        #
        #
        # vk = vk_session.get_api()

        # print(vk.wall.post(message='Hello world!'))
        vk.logger.setLevel('DEBUG')


        session = vk.Session(access_token=VK_APP_TOKEN)
        # print(f"session: {str(session)}")

        api_vk = vk.API(session)
        # print(f"api_vk: {str(api_vk)}")

        # get = api_vk.wall.get(owner_id=f"-{VK_UCA_GROUP_NUMBER}", v=VK_API_VERSION)
        # print(f"get: {str(get)}")



        if post.stored_file_urls is not None:

            print("Flag 03")
            path = post.stored_file_urls[0]
            path = str(os.path.join('..', path))

            # print(f"path: {path}")



            paths = ['img.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg', 'img6.jpg', 'img7.jpg', 'img8.png', 'gggg.gif', 'tttt.txt']

            if len(paths) > 10:
                logger.warning('Created post has more then 10 attachments! VK only allows 10 attachments per 1 post!')
                paths = paths[:10]

            attachments = []
            img_upload_url = None
            doc_upload_url = None


            for path in paths:
                if path.endswith('.jpg') or path.endswith('.png') or path.endswith('.jpeg'):
                    if not img_upload_url:
                        img_upload_url = self.get_img_upload_url()

                    # путь к вашему изображению
                    file = {'photo': (path, open(path, 'rb'))}

                    # Загружаем изображение на url
                    response = requests.post(img_upload_url, files=file)
                    result = json.loads(response.text)
                    print(f"result 2: {result}")

                    # Сохраняем фото на сервере и получаем id
                    data = api_vk.photos.saveWallPhoto(server=int(result['server']),
                                                       photo=result['photo'],
                                                       hash=result['hash'],
                                                       v=VK_API_VERSION
                                                       )

                    attachments.append(f"photo{VK_USER_ID}_{data[0]['id']}")

                elif path.endswith('.gif') or path.endswith('.giff') or path.endswith('.txt'):
                    if not doc_upload_url:
                        doc_upload_url = self.get_doc_upload_url()

                    # путь к вашему изображению
                    file = {'file': (path, open(path, 'rb'))}

                    # Загружаем изображение на url
                    response = requests.post(doc_upload_url, files=file)
                    result = json.loads(response.text)
                    print(f"result 2: {result}")
                    # Сохраняем фото на сервере и получаем id
                    data = api_vk.docs.save(file=result['file'],
                                            v=VK_API_VERSION
                                            )

                    attachments.append(f"doc{data['doc']['owner_id']}_{data['doc']['id']}")


            result = api_vk.wall.post(
                                      access_token=VK_APP_TOKEN,
                                      owner_id=-VK_UCA_GROUP_NUMBER,
                                      message='Hello world!',
                                      attachments=attachments,
                                      v=VK_API_VERSION
                                      )

            print(f"result 4: {result}")

            for a in attachments:
                if a.startswith('doc'):
                    ids = a[3:]
                    owner_id = ids.split('_')[0]
                    doc_id = ids.split('_')[1]
                    api_vk.docs.delete(owner_id=owner_id,
                                              doc_id=doc_id,
                                              v=VK_API_VERSION
                                              )




    def get_img_upload_url(self):
        # Получаем ссылку для загрузки изображений
        method_url = 'https://api.vk.com/method/photos.getWallUploadServer?'
        response = requests.post(method_url,
                                 dict(access_token=VK_APP_TOKEN,
                                      gid=VK_UCA_GROUP_NUMBER,
                                      v=VK_API_VERSION)
                                 )
        result = json.loads(response.text)
        return result['response']['upload_url']


    def get_doc_upload_url(self):
        method_url = 'https://api.vk.com/method/docs.getWallUploadServer?'
        response = requests.post(method_url,
                                 dict(access_token=VK_APP_TOKEN,
                                      gid=VK_UCA_GROUP_NUMBER,
                                      v=VK_API_VERSION)
                                 )
        result = json.loads(response.text)
        return result['response']['upload_url']







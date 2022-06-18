import json
import os
from io import BytesIO
from vk.exceptions import VkAPIError
from urllib3 import encode_multipart_formdata

from PIL import Image as PImage
import vk
from cassandra.cqlengine.management import sync_table

from credentials import VK_UCA_GROUP_TOKEN, VK_USER_LOGIN, VK_USER_PASSWORD, VK_UCA_GROUP_NUMBER, VK_USER_ID, \
    VK_APP_TOKEN, VK_APP_ID, VK_API_VERSION, VK_USER_TOKEN, VK_APP_PASSWORD
from loader.models import PostEntry, Compilation

import requests




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
        print(f"session: {str(session)}")

        api_vk = vk.API(session)
        print(f"api_vk: {str(api_vk)}")

        # get = api_vk.wall.get(owner_id=f"-{VK_UCA_GROUP_NUMBER}", v=VK_API_VERSION)
        # print(f"get: {str(get)}")



        if post.stored_file_urls is not None:
            # files_dir = os.path.dirname(post.stored_file_urls[0])

            # files = [files.extend(glob.glob(files_dir + '*.' + e)) for e in ext]
            #
            # images = [cv2.imread(file) for file in files]


            # loaded_images = []
            # for path in post.stored_file_urls:
            #     path = str(os.path.join('..', path))
            #     img = PImage.open(path)
            #     loaded_images.append(img)
            #
            # img = loaded_images[0]



            print("Flag 01")

            method_url = api_vk.photos\
                .getWallUploadServer(group_id=VK_UCA_GROUP_NUMBER,
                                     access_token=VK_APP_TOKEN,
                                     v=VK_API_VERSION
                                     )
            print("Flag 02")
            print(f"method_url: {method_url}")
            print(f"method_url['upload_url']: {method_url['upload_url']}")


            print("Flag 03")
            path = post.stored_file_urls[0]
            path = str(os.path.join('..', path))

            # print(f"path: {path}")


            response = requests.post(method_url['upload_url'],
                                     files={
                                         'file': ( 'image.jpg', open(path, 'rb'))
                                     })



            print("Flag 03")

            result = json.loads(response.text)
            print(f"response.text: {response.text}")
            print(f"result 0: {result}")

            response_text = response.text

            str1 = response_text.split(',"photo":')
            str2 = str1[1].split(',"hash":')

            server=result['server'],
            photo=str2[0],
            hash=result['hash']

            server2=result['server'],
            photo2=result['photo'],
            hash2=result['hash']


            # Сохраняем фото на сервере и получаем id

            response = api_vk.photos.saveWallPhoto(server=int(result['server']),
                                                   photo=photo,
                                                   hash=result['hash'],
                                                   v=VK_API_VERSION
                                                   )



            # method_url = 'https://api.vk.com/method/photos.saveWallPhoto?'
            # response = requests.post(method_url,
            #                          access_token=VK_APP_TOKEN,
            #                          gid=VK_UCA_GROUP_NUMBER,
            #                          v=VK_API_VERSION,
            #                          photo=result['photo'],
            #                          hash=result['hash'],
            #                          server=result['server']
            #                          )
            # result = json.loads(response.text)['response'][0]['id']
            result = json.loads(response.text)
            print(f"result 2: {result}")



            # Теперь этот id остается лишь прикрепить в attachments метода wall.post

            # vk.wall.post(owner_id=-VK_UCA_GROUP_NUMBER,
            #              message='Hello world!',
            #              attachments= "photo" + {owner_id} + "_" + {photo_id}
            #              v=VK_API_VERSION
            #              )

            method_url = 'https://api.vk.com/method/wall.post?'
            # response = requests.post(method_url,
            #                          owner_id=VK_UCA_GROUP_NUMBER,
            #                          v=VK_API_VERSION,
            #                          attachments=result,
            #                          message="Hello, world 2")
            # result = json.loads(response.text)


            # На выходе мы получим в ответе post_id если не было ошибки
            print(f"result 3: {result}")



        # api_vk.wall.post(owner_id=VK_UCA_GROUP_NUMBER,
        #                  v=VK_API_VERSION,
        #                  message="Hello, world")







        #
        #
        # session = vk.AuthSession(VK_APP_ID, VK_USER_ID, VK_USER_PASSWORD, scope='wall')
        # vk_api = vk.API(session)
        # print(vk_api.users.get(user_id=VK_USER_ID))
        #
        # # vk_api.wall.post(message="hello")












        # vk_session = vk_api.VkApi(VK_USER_LOGIN, VK_USER_PASSWORD)
        # vk_session.auth()
        #
        # vk = vk_session.get_api()
        #
        # print(vk.wall.post(message='Hello world!'))
        # # vk_api.exceptions.AuthError: No handler for two-factor authentication











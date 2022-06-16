import vk
from cassandra.cqlengine.management import sync_table

from credentials import VK_UCA_GROUP_TOKEN, VK_USER_LOGIN, VK_USER_PASSWORD, VK_UCA_GROUP_NUMBER, VK_USER_ID, \
    VK_APP_TOKEN, VK_APP_ID, VK_API_VERSION, VK_USER_TOKEN, VK_APP_PASSWORD
from loader.models import PostEntry, Compilation
from loader.utils import create_vk_session


# import vk as vk
import vk_api as vk_api


class VKLoader:

    def __init__(self):
        # self.client = Utils.create_vk_client()
        # self.session = create_vk_session()
        sync_table(PostEntry)
        sync_table(Compilation)


    def upload(self):
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

        get = api_vk.wall.get(owner_id=VK_UCA_GROUP_NUMBER, v=VK_API_VERSION)
        print(f"get: {str(get)}")

        api_vk.wall.post(owner_id=VK_UCA_GROUP_NUMBER, v=VK_API_VERSION, message="Hello, world")



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











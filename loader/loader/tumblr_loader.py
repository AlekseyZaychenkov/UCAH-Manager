import os

import pathlib
import pytumblr as pytumblr
from pathlib import Path



# documentation: https://openbase.com/python/PyTumblr/documentation
class TumblrLoader:

    def __init__(self, consumer_key, consumer_secret, oath_token, oath_secret):
        self.client = pytumblr.TumblrRestClient(
            consumer_key,
            consumer_secret,
            oath_token,
            oath_secret,
        )



    def get_from_anywhere(self, tags, blog=None):
        print(f"Getting posts from Tambler by tags '{tags}'")


        # TODO: figure out how to use offset
        offset = None

        for i in range(3):
            #response = client.posts(blog, limit=20, offset=offset, reblog_info=True, notes_info=True)
            print(f"Flag i: {i}")

            # TODO: try to move request out of cicle for
            # TODO: read all post in the blog for first version
            #  and check if posts with this original id already in cassandra
            # TODO: try to save all date with images

            # TODO: this oner read all posts. Try to use read only specific blog
            # TODO: read posts from top to botton

            # TODO: change 'paleontology' to list of tags
            response = self.client.tagged(tag='paleontology', limit=20) if blog == None \
                else client.posts(blog, limit=20, offset=offset, reblog_info=True, notes_info=True)
            print(f"response: {response}")





            print(f"<===== ===== =====  Parsing  ===== ===== =====>")

            for post in response:
                print(f"Post:"
                      f"\n{post}+\n\n")



                # if('photos' not in post):
                #     print(f"post: {post}")
                #     if('body' in post):
                #
                #         body = post['body']
                #         body = body.split('<')
                #         print(f"Flag 01: type(body): {type(body)}")
                #         print(f"Flag 01: body: {body}")
                #
                #         body = [b for b in body if 'img src=' in b]
                #         print(f"Flag 02: body: {body}")
                #         if(body):
                #             images = list()
                #             for b in body:
                #                 if type(b)==list and len(b) >= 2:
                #                     images.append(b[1])
                #
                #             body = body[0].split('\'')
                #
                #             print(f"Flag 03: images: {images}")
                #             if images:
                #                 yield images
                #         else:
                #             print(f"Flag 04 (else): {body}")
                #         yield
                #
                #
                # else:
                #     print(f"post['photos'][0]['original_size']['url']: {post['photos'][0]['original_size']['url']}")
                #
                #     yield post['photos'][0]['original_size']['url']


            # move to the next offset
            offset = response[-1]['timestamp']
        print(offset)


    def get_from_blog(self, tags, blog):
        print(f"Getting posts from Tambler blog '{blog}'")

        # TODO: implement realization
        for i in range(3):
            #response = client.posts(blog, limit=20, offset=offset, reblog_info=True, notes_info=True)
            print(f"Flag i: {i}")
            # self.client.posts(tag = tags)




    def download(self, tags, blogs=None):

        if blogs and len(blogs) > 0:
            # self.get_all_posts(blog, tags)


            for blog in blogs:
                blogsName = pathlib.PurePath(blog).name

                curpath = os.path.abspath(os.curdir)
                strFullPath = os.path.join(curpath, f"{blogsName}-posts.txt")

                print(f"Trying to create or rewrite file '{strFullPath}'")
                fullPath = Path(strFullPath)
                fullPath.touch(exist_ok=True)  # will create file, if it exists will do nothing

                with open(fullPath, "w+") as out_file:
                    for post in self.get_from_blog(blog, tags):
                        print(post, file=out_file)
        else:

            curpath = os.path.abspath(os.curdir)
            strFullPath = os.path.join(curpath, f"tags--{'_'.join(tags)}-posts.txt")

            print(f"Trying to create or rewrite file '{strFullPath}'")
            fullPath = Path(strFullPath)
            fullPath.touch(exist_ok=True)  # will create file, if it exists will do nothing

            with open(fullPath, "w+") as out_file:
                for post in self.get_from_anywhere(tags):
                    print(post, file=out_file)








    # def download(self):
    #
    #     print("Authorization URL"
    #           f"\n~~~~~~~~~~~~~~~~~~~~~")
    #
    #     t = Tumblpy(TumblrLoader.CONSUMER_KEY, TumblrLoader.CONSUMER_SECRET)
    #     auth_props = t.get_authentication_tokens(callback_url='http://michaelhelmick.com')
    #
    #     auth_url = auth_props['auth_url']
    #     print(f"auth_url: {auth_url}")
    #     OAUTH_TOKEN_SECRET = auth_props['oauth_token_secret']
    #     print(f"OAUTH_TOKEN_SECRET: {OAUTH_TOKEN_SECRET}")
    #     print(f"str(auth_props): {str(auth_props)}")
    #     print(f"oauth_callback_confirmedL: {str(auth_props['oauth_callback_confirmed'])}")
    #
    #
    #     print(f"Connect with Tumblr via:  % {auth_url}")
    #
    #
    #     print(f"Handling the Callback"
    #           f"\n~~~~~~~~~~~~~~~~~~~~~")
    #     # .. code-block:: python
    #
    #     # OAUTH_TOKEN_SECRET comes from the previous step
    #     # if needed, store those in a session variable or something
    #
    #     # oauth_verifier and OAUTH_TOKEN are found in your callback url querystring
    #     # In Django, you'd do something like:
    #     OAUTH_TOKEN = request.urlopen(auth_url)
    #     oauth_verifier = request.urlopen(auth_url)
    #
    #     print(f"OAUTH_TOKEN: {OAUTH_TOKEN}")
    #     print(f"oauth_verifier: {oauth_verifier}")
    #
    #
    #     t = Tumblpy(TumblrLoader.CONSUMER_KEY, TumblrLoader.CONSUMER_SECRET,
    #                 OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    #
    #     print(f"t: {str(t)}")
    #
    #     authorized_tokens = t.get_authorized_tokens(oauth_verifier)
    #
    #     print(f"authorized_tokens: {str(authorized_tokens)}")
    #
    #     final_oauth_token = authorized_tokens['oauth_token']
    #     final_oauth_token_secret = authorized_tokens['oauth_token_secret']
    #
    #     print(f"final_oauth_token: {final_oauth_token}")
    #     print(f"final_oauth_token_secret: {final_oauth_token_secret}")
    #
    #
    #     # Save those tokens to the database for a later use?
    #     # TODO: implement method for saving tokens







        # print("Getting some User information"
        #       "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # .. code-block:: python

        # Get the final tokens from the database or wherever you have them stored

        # t = Tumblpy(TumblrLoader.CONSUMER_KEY, TumblrLoader.CONSUMER_SECRET,
        #             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        #
        #
        #
        # # Print out the user info, let's get the first blog url...
        # blog_url = t.post('user/info')
        # print(f"blog_url: {blog_url}")
        #
        # blog_url = blog_url['user']['blogs'][0]['url']
        # print(f"blog_url_2: {blog_url}")


        # print("Getting posts from a certain blog"
        #       "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        # .. code-block:: python
        #
        # # Assume you are using the blog_url and Tumblpy instance from the previous section\


        # posts = t.get('posts', blog_url=blog_url)
        # print posts
        # # or you could use the `posts` method
        # audio_posts = t.posts(blog_url, 'audio')
        # print audio_posts
        # all_posts = t.posts(blog_url)
        # print all_posts
        #
        # Creating a post with a photo
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ::
        #
        # # Assume you are using the blog_url and Tumblpy instance from the previous sections
        #
        # photo = open('/path/to/file/image.png', 'rb')
        # post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': 'Test Caption', 'data': photo})
        # print post # returns id if posted successfully
        #


        # Posting an Edited Photo *(This example resizes a photo)*
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        # .. code-block:: python
        #
        # # Assume you are using the blog_url and Tumblpy instance from the previous sections
        #
        # # Like I said in the previous section, you can pass any object that has a
        # # read() method
        #
        # # Assume you are working with a JPEG
        #
        # from PIL import Image
        # from StringIO import StringIO
        #
        # photo = Image.open('/path/to/file/image.jpg')
        #
        # basewidth = 320
        # wpercent = (basewidth / float(photo.size[0]))
        # height = int((float(photo.size[1]) * float(wpercent)))
        # photo = photo.resize((basewidth, height), Image.ANTIALIAS)
        #
        # image_io = StringIO.StringIO()
        # photo.save(image_io, format='JPEG')
        #
        # image_io.seek(0)
        #
        # try:
        #     post = t.post('post', blog_url=blog_url, params={'type':'photo', 'caption': 'Test Caption', 'data': photo})
        # print post
        # except TumblpyError, e:
        # # Maybe the file was invalid?
        # print e.message
        #


        # Following a user
        # ~~~~~~~~~~~~~~~~
        #
        # .. code-block:: python
        #
        # # Assume you are using the blog_url and Tumblpy instance from the previous sections
        # try:
        #     follow = t.post('user/follow', params={'url': 'tumblpy.tumblr.com'})
        # except TumblpyError:
        # # if the url given in params is not valid,
        # # Tumblr will respond with a 404 and Tumblpy will raise a TumblpyError
        #
        # Get a User Avatar URL *(No need for authentication for this method)*
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        # .. code-block:: python
        #
        # t = Tumblpy()
        # avatar = t.get_avatar_url(blog_url='tumblpy.tumblr.com', size=128)
        # print avatar['url']
        #
        # # OR
        #
        # avatar = t.get('avatar', blog_url='tumblpy.tumblr.com', extra_endpoints=['128'])
        # print avatar['url']
        #
        # Catching errors
        # ~~~~~~~~~~~~~~~
        #
        # .. code-block:: python
        #
        # try:
        #     t.post('user/info')
        # except TumbplyError, e:
        # print e.message
        # print 'Something bad happened :('
        #
        # Thanks for using Tumblpy!
        #
        #
        # .. :changelog:
        #
        # History
        # -------
        #
        # 1.1.4 (2016-02-08)
        # ++++++++++++++++++
        #
        # - Remove old api url string formatting.
        # - Added ``posts`` method to Tumblpy, see README for example.
        #
        # 1.1.3 (2016-01-17)
        # ++++++++++++++++++
        #
        # - Fix missing import
        #
        # 1.1.2 (2016-12-22)
        # ++++++++++++++++++
        #
        # - Fix missing import
        #
        # 1.1.1 (2016-05-12)
        # ++++++++++++++++++
        #
        # - Fix issue where blogs using https:// were being parsed wrong
        #
        #
        # 1.1.0 (2016-30-04)
        # ++++++++++++++++++
        #
        # - Add following and dashboard API methods
        #
        #
        # 1.0.5 (2015-08-13)
        # ++++++++++++++++++
        #
        # - Add support for ``proxies`` keyword for requests
        #
        #
        # 1.0.4 (2015-01-15)
        # ++++++++++++++++++
        #
        # - Fix request token decode issue in Python 3
        #
        #
        # 1.0.3 (2014-10-17)
        # ++++++++++++++++++
        #
        # - Unpin ``requests`` and ``requests-oauthlib`` versions in ``setup.py``
        #
        #
        # 1.0.2 (2013-05-31)
        # ++++++++++++++++++
        #
        # - Made the hotfix for posting photos a little more hotfixy... fixed posting just regular posts (as well as photos)
        #
        # 1.0.1 (2013-05-29)
        # ++++++++++++++++++
        #
        # - Hotfix image uploading (not sure why we have to pass ``params`` AND ``data`` to the POST, hotfix for the time being...)
        # - Allow for ints and floats (and longs in Python 2) to be passed as parameters to Tumblpy Tumblr API functions
        #
        #
        # 1.0.0 (2013-05-23)
        # ++++++++++++++++++
        #
        # - Changed internal Tumblpy API structure, but Tumblpy functions should still work as they did before
        # - Updated README with more clear examples
        # - Added LICENSE
        # - ``_split_params_and_files`` has been moved to ``helpers.py``
        # - All ``Tumblpy`` exceptions are found in ``exceptions.py``
        # - Removed ``pool_maxsize`` from ``Tumblpy.__init__`` because it wasn't being used
        # - Removed ``timeout`` parameter from all request methods for the time being
        # - Removed ``TumblpyTimeout`` Exception
        # - Moved ``callback_url`` parameter from ``Tumblpy.__init__`` to ``get_authentication_tokens``
        # - All authentication and API calls over HTTPS
        # - Dropped Python 2.5 support
        # - Full, transparent Python 3.3 support








import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from UCA_Manager.settings import AUTH_USER_MODEL

import sys
sys.path.append("../../loader")


#  TODO: to figure out, what object type to use for translating search queries from user to backand application
class ExampleModel(Model):
    example_id            = columns.UUID(primary_key=True, default=uuid.uuid4)
    example_type          = columns.Integer(index=True)
    created_at            = columns.DateTime()
    description           = columns.Text(required=False)


class PostEntry(Model):
    id                    = columns.UUID(primary_key=True, default=uuid.uuid4)

    # information about original post
    blog_name             = columns.Text(max_length=50, required=True)
    blog_url              = columns.Text(max_length=2048, required=True)
    id_in_social_network  = columns.BigInt(required=False, index=True)
    url                   = columns.Text(max_length=2048, required=True)
    posted_date           = columns.Text(max_length=30)
    posted_timestamp      = columns.Integer(required=False, index=True)
    tags                  = columns.List(value_type=columns.Text, required=True)
    text                  = columns.Text(required=False)
    file_urls             = columns.List(value_type=columns.Text, required=False)  # list of urls

    # information about search query parameters
    compilation_id        = columns.UUID(required=False)

    # information for posting
    stored_file_urls      = columns.List(value_type=columns.Text, required=False)  # list of local paths or urls do download
    external_link_urls    = columns.List(value_type=columns.Text, required=False)

    # information for administration notes and file storing
    description           = columns.Text(required=False)

    # information about posting
    # # TODO: implement special map-like structure for storing published posts with statistic about them (postUrl1, likes, comments, likes under comments)
    # where_posted        = columns.Map(key_type=columns.Text, value_type=columns.Text, required=False)  # list of dicts "blogName: {'dateTime1 - postUrl1', 'dateTime2 - postUrl2', ...}"


class Compilation(Model):
    id                    = columns.UUID(primary_key=True, default=uuid.uuid4)

    name                  = columns.Text(max_length=512, required=False)

    resource              = columns.Text(max_length=64, required=False)
    search_tag            = columns.Text(max_length=512, required=False)
    search_blogs          = columns.List(value_type=columns.Text, required=False)
    update_date           = columns.Text(max_length=30, required=True, index=True)
    description           = columns.Text(required=False)
    storage               = columns.Text(max_length=2048, required=False)

    post_ids              = columns.List(value_type=columns.UUID, required=False)



#  From eco:

def upload_location(instance, filename, **kwargs):
    file_path = 'profile_images/{filename}'.format(
        filename=hashlib.md5(str(instance.email).encode()).hexdigest() + os.path.splitext(filename)[1]
    )
    return file_path

# @receiver(post_save, sender=AUTH_USER_MODEL)
# def post_save_compress_img(sender, instance, *args, **kwargs):
#     if instance.profile_img:
#         picture = Image.open(instance.profile_img.path)
#         picture.save(instance.profile_img.path, optimize=True, quality=30)
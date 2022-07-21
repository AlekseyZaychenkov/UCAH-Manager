import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from UCA_Manager.settings import AUTH_USER_MODEL

import sys
sys.path.append("../../loader")


class Post(Model):
    id                    = columns.UUID(primary_key=True, default=uuid.uuid4)

    # information about original post
    blog_name             = columns.Text(max_length=50, required=True)
    blog_url              = columns.Text(max_length=2048, required=True)
    # TODO: rename to id_in_resource
    id_in_social_network  = columns.BigInt(required=False, index=True)
    original_post_url     = columns.Text(max_length=2048, required=False)
    posted_date           = columns.Text(max_length=30)
    posted_timestamp      = columns.Integer(required=False, index=True)
    tags                  = columns.List(value_type=columns.Text, required=False)
    text                  = columns.Text(required=False)
    file_urls             = columns.List(value_type=columns.Text, required=False)

    # information about search query parameters
    compilation_id        = columns.UUID(required=False, primary_key=True, clustering_order="ASC")

    # information for posting
    # TODO: rename to stored_file_paths
    stored_file_urls      = columns.List(value_type=columns.Text, required=False)  # list of local paths or urls do download
    # TODO: rename to external_links
    external_link_urls    = columns.List(value_type=columns.Text, required=False)


    # information for administration notes and file storing
    description           = columns.Text(required=False)


    # information after posted
    url                   = columns.Text(max_length=2048, required=False)


class Compilation(Model):
    id                    = columns.UUID(primary_key=True, default=uuid.uuid4)

    name                  = columns.Text(max_length=512, required=False)

    resource              = columns.Text(max_length=64, required=False)
    # TODO: search_tags = columns.List(value_type=columns.Text, required=False)
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

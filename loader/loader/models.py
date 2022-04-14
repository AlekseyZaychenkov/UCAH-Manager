import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

import sys
sys.path.append("..")


#  TODO: to figure out, what object type to use for translating search queries from user to backand application
class ExampleModel(Model):
    example_id      = columns.UUID(primary_key=True, default=uuid.uuid4)
    example_type    = columns.Integer(index=True)
    created_at      = columns.DateTime()
    description     = columns.Text(required=False)


class PostEntry(Model):
    id                           = columns.UUID(primary_key=True, default=uuid.uuid4)

    # information about original post
    original_blog_name           = columns.Text(max_length=50, required=True)
    original_blog_url            = columns.Text(max_length=2048, required=True)
    original_post_id             = columns.BigInt(required=False, index=True)
    original_post_url            = columns.Text(max_length=2048, required=True)
    original_posted_date         = columns.Text(max_length=30)
    original_posted_timestamp    = columns.Integer(required=False, index=True)
    original_post_tags           = columns.List(value_type=columns.Text, required=True)
    original_text                = columns.Text(required=False)
    original_file_urls           = columns.List(value_type=columns.Text, required=False)  # list of urls
    original_external_link_urls  = columns.List(value_type=columns.Text, required=False)  # list of urls to external resoueces for instance youtube

    # information about search query parameters
    compilation_id               = columns.UUID(required=True)

    # information for posting
    text                         = columns.Text(required=False)
    file_urls                    = columns.List(value_type=columns.Text, required=False)  # list of local paths or urls do download
    external_link_urls           = columns.List(value_type=columns.Text, required=False)

    # information for administration notes and file storing
    description                  = columns.Text(required=False)

    # information about posting
    # TODO: implement special map-like structure for storing published posts with statistic about them (postUrl1, likes, comments, likes under comments)
    where_posted                 = columns.Map(key_type=columns.Text, value_type=columns.Text, required=False)  # list of dicts "blogName: {'dateTime1 - postUrl1', 'dateTime2 - postUrl2', ...}"


class Compilation(Model):
    id                           = columns.UUID(primary_key=True, default=uuid.uuid4)

    original_resource            = columns.Text(max_length=20, required=False)
    search_tag                   = columns.Text(max_length=512, required=False)
    search_blogs                 = columns.List(value_type=columns.Text, required=False)
    downloaded_date              = columns.Text(max_length=30, required=True, index=True)
    description                  = columns.Text(required=False)
    storage                      = columns.Text(max_length=2048, required=False)

    post_ids                     = columns.List(value_type=columns.UUID, required=False)

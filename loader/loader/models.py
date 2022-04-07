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
    id                        = columns.UUID(primary_key=True, default=uuid.uuid4)

    # information about original post
    originalResource          = columns.Text(max_length=20, required=False)
    originalBlogName          = columns.Text(max_length=50, required=True)
    originalBlogUrl           = columns.Text(max_length=250, required=True)
    originalPostId            = columns.BigInt(required=False, index=True)
    originalPostUrl           = columns.Text(max_length=250, required=True)
    originalPostedDate        = columns.Text(max_length=30)
    originalPostTags          = columns.List(value_type=columns.Text, required=True)
    originalText              = columns.Text(required=False)
    originalFileUrls          = columns.List(value_type=columns.Text, required=False)  # list of urls
    originalExternalLinkUrls  = columns.List(value_type=columns.Text, required=False)  # list of urls to external resoueces for instance youtube

    # information about search query parameters
    searchTags                = columns.List(value_type=columns.Text, required=False)
    downloatedDate            = columns.Text(max_length=30, required=True)

    # information for posting
    text                      = columns.Text(required=False)
    fileUrls                  = columns.List(value_type=columns.Text, required=False)  # list of local paths or urls do download
    externalLinkUrls          = columns.List(value_type=columns.Text, required=False)

    # information for administration notes and file storing
    description               = columns.Text(required=False)
    storage                   = columns.Text(max_length=500, required=True)

    # information about posting
    # TODO: implement special map-like structure for storing published posts with statistic about them (postUrl1, likes, comments, likes under comments)
    wherePosted               = columns.Map(key_type=columns.Text, value_type=columns.Text, required=False)  # list of dicts "blogName: {'dateTime1 - postUrl1', 'dateTime2 - postUrl2', ...}"

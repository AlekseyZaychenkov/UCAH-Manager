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


class TumblerCredentials(Model):
    id              = columns.UUID(primary_key=True, default=uuid.uuid4)
    example_type    = columns.Integer(index=True)
    created_at      = columns.DateTime()
    description     = columns.Text(required=False)


class PostEntry(Model):
    id                  = columns.UUID(primary_key=True, default=uuid.uuid4)

    # information about original post
    originalResource    = columns.CharField(max_length=20, required=False)
    originalBlogName    = columns.CharField(max_length=20, required=True)
    originalBlogUrl     = columns.CharField(max_length=50, required=True)
    originalId          = columns.Integer(required=False)
    originalUrl         = columns.CharField(max_length=50, required=True)
    originalPostedDate  = columns.DateTime()
    originalPostTags    = columns.CharField(max_length=1000, required=True)
    originalText        = columns.Text(required=False)
    originalImageUrls   = models.Text(required=False)  # list of urls

    # information about search query parameters
    searchTags          = columns.CharField(max_length=200, required=True)
    downloatedDate      = columns.DateTime(default=datetime.now)

    # information for posting
    text                = columns.Text(required=False)
    imageUrls           = models.Text(required=False)  # list of local paths or urls do download

    # information for administration notes
    description         = columns.Text(required=False)

    # information about posting
    wherePosted         = columns.Text(required=False)  # list of dicts "blogName: {'dateTime1 - postUrl1', 'dateTime2 - postUrl2', ...}"

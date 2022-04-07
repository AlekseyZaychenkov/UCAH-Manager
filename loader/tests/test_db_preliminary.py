import os

from django.test import SimpleTestCase
from datetime import datetime
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table
from cassandra.cqlengine import connection
from utils import Utils

import sys
sys.path.append("..")
from models import ExampleModel

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


class Test_DB(SimpleTestCase):

    def test_writing_and_reading(self):
        Utils.startSession()

        drop_table(ExampleModel)
        sync_table(ExampleModel)

        # TODO: change to real objects
        em1 = ExampleModel.create(example_type=0, description="example1", created_at=datetime.now())
        em2 = ExampleModel.create(example_type=0, description="example2", created_at=datetime.now())
        em3 = ExampleModel.create(example_type=0, description="example3", created_at=datetime.now())
        em4 = ExampleModel.create(example_type=0, description="example4", created_at=datetime.now())
        em5 = ExampleModel.create(example_type=1, description="example5", created_at=datetime.now())
        em6 = ExampleModel.create(example_type=1, description="example6", created_at=datetime.now())
        em7 = ExampleModel.create(example_type=1, description="example7", created_at=datetime.now())
        em8 = ExampleModel.create(example_type=1, description="example8", created_at=datetime.now())

        ExampleModel.objects.count()
        q = ExampleModel.objects(example_type=1)
        assert q.count() == 4

        descriptions = list()
        for instance in q:
            descriptions.append(instance.description)
        assert sorted(descriptions) == sorted(['example5', 'example6', 'example8', 'example7'])


        descriptions2 = list()
        q2 = q.filter(example_id=em5.example_id)
        assert q2.count() == 4

        for instance in q2:
            descriptions2.append(instance.description)
        assert sorted(descriptions2) == sorted(list(['example5']))

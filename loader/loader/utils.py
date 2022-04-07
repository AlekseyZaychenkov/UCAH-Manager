from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table

import sys
sys.path.append("..")
from loader.loader.settings import IS_TEST, DB_ADRESSES, TEST_KEYSPACE_NAME, KEYSPACE_NAME


class Utils:

    @staticmethod
    def startSession():
        if IS_TEST:
            connection.setup(DB_ADRESSES.split(","), TEST_KEYSPACE_NAME, protocol_version=3)
        else:
            connection.setup(DB_ADRESSES.split(","), KEYSPACE_NAME, protocol_version=3)


    @staticmethod
    def syncModels():
        sync_table(ExampleModel)
        sync_table(TumblerCredentials)


    @staticmethod
    def dropModels():
        drop_table(ExampleModel)
        drop_table(TumblerCredentials)




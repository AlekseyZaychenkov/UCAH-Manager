from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.management import drop_table

import sys
sys.path.append("../../loader")
from account.settings import IS_TEST, CASSANDRA_DB_ADRESSES, TEST_CASSANDRA_KEYSPACE_NAME, CASSANDRA_KEYSPACE_NAME


class Utils:

    @staticmethod
    def startSession():
        if IS_TEST:
            connection.setup(CASSANDRA_DB_ADRESSES.split(","), TEST_CASSANDRA_KEYSPACE_NAME, protocol_version=3)
        else:
            connection.setup(CASSANDRA_DB_ADRESSES.split(","), CASSANDRA_KEYSPACE_NAME, protocol_version=3)


    @staticmethod
    def syncModels():
        sync_table(ExampleModel)
        sync_table(PostEntry)
        sync_table(Compilation)


    @staticmethod
    def dropModels():
        drop_table(ExampleModel)
        drop_table(PostEntry)
        drop_table(Compilation)




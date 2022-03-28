from cassandra.cqlengine import connection

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

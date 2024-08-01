import unittest
from qdrant_connector.src.qdrant_connection_params import QdrantConnectionParams, ConnType


class QdrantConnectionParamsTest(unittest.TestCase):
    """
    unit tests for the qdrant connection params
    """

    def test_memory_type(self):
        """
        test the memory type
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        self.assertEqual(conn_type.url, ":memory:", "not memory type")  # add assertion here

    def test_local_type(self):
        """
        test the local connection
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.LOCAL, url="http://localhost:6333")
        self.assertEqual(conn_type.url, "http://localhost:6333", "wrong connection url")  # add assertion here
        self.assertEqual(conn_type._type, ConnType.LOCAL, "wrong connection type")


if __name__ == '__main__':
    unittest.main()

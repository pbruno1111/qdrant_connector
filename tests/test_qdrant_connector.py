import unittest
import uuid

from qdrant_connector.src.data.entity import EntityData, EntityId, Entity
from qdrant_connector.src.data.field import FieldData, Field
from qdrant_connector.src.data.index import IndexConfig
from qdrant_connector.src.qdrant_connector import QdrantConnector
from qdrant_connector.src.qdrant_connection_params import QdrantConnectionParams, ConnType
from qdrant_client.models import Distance
from qdrant_connector.tests.helper.helper import TestHelper


class QdrantConnectorTest(unittest.TestCase):
    """
    Unit tests for the qdrant connector
    """

    def create_data(self):
        """
        create sample data to be used in the tests
        :return:
        """
        self.entity_data_list = []
        field_data_list1 = []
        field_data_list2 = []
        field_data11 = FieldData(name="f11", value="abdd11")
        field_data12 = FieldData(name="f12", value="abdd12")
        field_data_list1.append(field_data11)
        field_data_list1.append(field_data12)
        field_data21 = FieldData(name="f21", value="abdd21")
        field_data22 = FieldData(name="f22", value="abdd22")
        field_data_list2.append(field_data21)
        field_data_list2.append(field_data22)
        entity_data1 = EntityData(entity_id=EntityId(object_id='1', schema_id='0'), field_data=field_data_list1)
        entity_data2 = EntityData(entity_id=EntityId(object_id='2', schema_id='0'), field_data=field_data_list2)
        self.entity_data_list.append(entity_data1)
        self.entity_data_list.append(entity_data2)
        self.entity_list = []
        field_list1 = []
        field1 = Field(name='f11')
        field_list1.append(field1)
        entity1 = Entity(entity_id=EntityId(object_id='1', schema_id='0'), fields=field_list1)
        self.entity_list.append(entity1)

    def create_random_data(self):
        """
        create randomized data to be used in the tests
        :return:
        """
        self.entity_list = [TestHelper.create_random_entity() for _ in range(10)]
        self.entity_data_list = [TestHelper.create_random_entity_data() for _ in range(10)]
        self.query_vector = TestHelper.vector_generator()
        self.field_list = []
        for f in self.entity_data_list[0].field_data:
            self.field_list.append(Field(name=f.name, data_type=f.data_type))

    def test_create_index(self):
        """
        test the index creation
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        idx2 = IndexConfig(index_name="test2", config_data={'size': 100, 'distance': Distance.COSINE})
        index_confs.append(idx1)
        index_confs.append(idx2)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        connector.create_index(index_config=idx1)
        self.assertEqual(connector._check_collections()[0].name, 'test1', "wrong index name")
        connector.drop_index(index_name="test1")

    def test_drop_index(self):
        """
        test index drop
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        idx2 = IndexConfig(index_name="test2", config_data={'size': 100, 'distance': Distance.COSINE})
        index_confs.append(idx1)
        index_confs.append(idx2)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        connector.create_index(index_config=idx1)
        connector.create_index(index_config=idx2)
        connector.drop_index(index_name="test2")
        self.assertEqual(connector._check_collections()[0].name, "test1", "wrong index name")
        connector.drop_index(index_name="test1")

    def test_write_entities(self):
        """
        test write entities
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        idx2 = IndexConfig(index_name="test2", config_data={'size': 100, 'distance': Distance.COSINE})
        index_confs.append(idx1)
        index_confs.append(idx2)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        connector.create_index(index_config=idx1)
        self.assertEqual(connector._check_collections()[0].name, "test1", "wrong index name")
        self.create_random_data()
        connector.write_entities(entity_data=self.entity_data_list)
        sample_id = connector._scroll(index_name="test1")[0][0].id
        found = False
        for e in self.entity_data_list:
            if str(sample_id) == str(e.entity_id.object_id):
                found = True
        self.assertEqual(found, True,"id not found")
        connector.drop_index(index_name="test1")

    def test_read_entities(self):
        """
        test read entities
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        idx2 = IndexConfig(index_name="test2", config_data={'size': 100, 'distance': Distance.COSINE})
        index_confs.append(idx1)
        index_confs.append(idx2)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        connector.create_index(index_config=idx1)
        self.assertEqual(connector._check_collections()[0].name, "test1", "wrong index name")
        self.create_random_data()
        connector.write_entities(entity_data=self.entity_data_list)
        entities = connector.read_entities(self.entity_list)
        self.assertEqual(len(entities), len(self.entity_list), "not enough entities read")
        connector.drop_index(index_name="test1")

    def test_search(self):
        """
        test simple vector search
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        idx2 = IndexConfig(index_name="test2", config_data={'size': 100, 'distance': Distance.COSINE})
        index_confs.append(idx1)
        index_confs.append(idx2)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        connector.create_index(index_config=idx1)
        self.assertEqual(connector._check_collections()[0].name, "test1", "wrong index name")
        self.create_random_data()
        connector.write_entities(entity_data=self.entity_data_list)
        self.assertEqual(len(connector.search(index_name="test1", vector=self.query_vector, returned_fields=self.field_list, limit=1)), 1, "no search results")
        connector.drop_index(index_name="test1")

    def test_simple_e2e(self):
        """
        simple end-to-end test
        :return:
        """
        self.create_data()
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        index_confs.append(idx1)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        self.assertEqual(len(connector._check_collections()), 0, "collections exists on start")
        connector.create_index(index_config=idx1)
        self.assertEqual(len(connector._check_collections()), 1, "collection not created")
        connector.write_entities(entity_data=self.entity_data_list)
        entities = connector.read_entities(entities=self.entity_list)
        self.assertEqual(len(entities), 1, "no entities returned")

        connector.drop_index(index_name="test1")
        self.assertEqual(len(connector._check_collections()), 0, "collection not deleted")
        connector._close_connection()

    def test_connection(self):
        """
        test qdrant connection
        :return:
        """
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        index_confs.append(idx1)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        self.assertNotEqual(connector._client, None, "connection not created")
        self.assertEqual(len(connector._check_collections()), 0, "collections exists on start")
        connector._close_connection()

    def test__get_object_id(self):
        conn_type = QdrantConnectionParams(conn_type=ConnType.MEMORY)
        index_confs = []
        idx1 = IndexConfig(index_name="test1", config_data={'size': 10, 'distance': Distance.DOT})
        index_confs.append(idx1)
        connector = QdrantConnector(connection_params=conn_type, index_configs=index_confs)
        self.assertEqual(type(connector._get_object_id("123")) is int, True, "wrong object id type")
        self.assertEqual(type(connector._get_object_id(str(uuid.uuid4()))) is str, True, "wrong object id type")


if __name__ == '__main__':
    unittest.main()

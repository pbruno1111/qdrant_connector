from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams
from qdrant_client.models import Filter, FieldCondition, MatchValue


from qdrant_connector.src.data.entity import Entity, EntityData
from qdrant_connector.src.data.field import Field, FieldData
from qdrant_connector.src.data.index import IndexConfig
from qdrant_connector.src.qdrant_connection_params import QdrantConnectionParams


class QdrantConnector:
    """
    Qdrant vector db connector
    """

    def __init__(self, connection_params: QdrantConnectionParams, index_configs: list[IndexConfig]) -> None:
        """
        Creates a qdrant connector
        :param connection_params: connection params, e.g. url and type
        :param index_configs: list of index configs to use
        """
        self._client = None
        self._connect(connection_params)
        self._index_configs: dict[str, IndexConfig] = {
            index_config.index_name: index_config
            for index_config in (index_configs or [])
        }
        self._collection_name = None

    def _connect(self, connection_params: QdrantConnectionParams) -> None:
        """
        internal, create connection to Qdrant
        :param connection_params: connection params, e.g. url and type
        :return: qdrant client with the opened connection
        """
        self._client = QdrantClient(connection_params.url)

    def _close_connection(self) -> None:
        """
        internal TODO
        :return:
        """
        # nothing to close in local in-memory qdrant
        pass

    def _create_search_index(self, index_config: IndexConfig) -> None:
        """
        internal create a search index
        :param index_config: index config for name and vector params
        :return:
        """
        self._index_configs[index_config.index_name] = index_config
        self._client.create_collection(collection_name=index_config.index_name,
                                       vectors_config=
                                       VectorParams(size=index_config.config_data['size'],
                                                    distance=index_config.config_data['distance']),
                                       )
        self._collection_name = index_config.index_name

    def _check_collections(self) -> list:
        """
        internal helper to check created collections
        :return:
        """
        return self._client.get_collections().collections

    def _drop_search_index(self, index_name: str) -> bool:
        """
        internal drop the create search index
        :param index_name: the name of the index to drop
        :return: success state
        """
        return self._client.delete_collection(index_name)

    def _get_object_id(self, object_id: str) -> Any:
        """
        internal fix the object id type for qdrant as it requires integers if the value is an integer
        otherwise use uuid
        :param object_id: the raw object id data
        :return: the object id using the right type
        """
        # if the object id represents only an integer, use it as an integer, if uuid string,
        # then it can be used as is
        try:
            if str(int(object_id)) == object_id:
                object_id = int(object_id)
        except ValueError:
            pass
        return object_id

    def _upsert(self, payload: list[dict]) -> None:
        """
        internal upsert data into collection
        :param payload: all the data to be inserted including text payload and vectors
        :return:
        """
        points = []
        for item in payload:
            object_id = self._get_object_id(object_id=item['object_id'])
            point = PointStruct(id=object_id, vector=item['vector'], payload=item)
            points.append(point)
        self._client.upsert(collection_name=self._collection_name,
                            wait=True,
                            points=points
                            )

    def _scroll(self, index_name: str) -> Any:
        """
        internal helper to scroll all data of a given collection
        :param index_name: the collection to check
        :return: the data stored in the collection with payload, without vectors and any filtering
        """
        return self._client.scroll(
            collection_name=index_name,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

    def create_index(self, index_config: IndexConfig) -> None:
        """
        create_index to create an index
        :param index_config: the index config to be used
        :return:
        """
        self._create_search_index(
            index_config
        )

    def drop_index(self, index_name: str) -> None:
        """
        drop_index to drop the index based on its name
        :param index_name: the name of the index to be dropped
        :return:
        """
        self._drop_search_index(index_name)
        del self._index_configs[index_name]

    def _read_entity(self, entity: Entity) -> EntityData:
        """
        internal helper to read 1 entity
        :param entity: the entity to be read
        :return: the entity data returned from the index
        """
        object_id = self._get_object_id(object_id=entity.entity_id.object_id)
        points = self._client.retrieve(collection_name=self._collection_name,
                                       ids=[object_id]
                                       )
        fields = []
        for point in points:
            vector = point.vector
            payload = point.payload
            has_vector_field = False
            for field in entity.fields:
                if field.data_type == "vector":
                    has_vector_field = True
                if field.name in payload:
                    fields.append(FieldData(name=field.name, value=payload[field.name]))
            if not has_vector_field:
                fields.append(FieldData(name="vector", data_type="vector", value=vector))
        return EntityData(entity_id=entity.entity_id, field_data=fields)

    def read_entities(self, entities: list[Entity]) -> list[EntityData]:
        """
        read_entities to read entities from an index with the list of fields described in te entities list
        :param entities: list of entities describing what should the returned data contain
        :return: list of entity data returned from the index
        """
        return [self._read_entity(entity) for entity in entities if entity.fields]

    def write_entities(self, entity_data: list[EntityData]) -> None:
        """
        write_entities to write entity data into the index
        :param entity_data: the entity data to be written into the index
        :return:
        """
        if not entity_data:
            return
        payload = []
        for e in entity_data:
            payload_item = {}
            object_id = e.entity_id.object_id
            payload_item['object_id'] = object_id
            for item in e.field_data:
                if item.data_type == "vector":
                    payload_item['vector'] = item.value
                else:
                    payload_item[item.name] = item.value
            if 'vector' not in payload_item or len(payload_item['vector']) < 1:
                payload_item['vector'] = [0.0]
            payload.append(payload_item)
        self._upsert(payload)

    def _search(self, index_name: str, vector: list[float], limit: int, search_filter: Filter = None) -> Any:
        """
        internal search with given criteria
        :param index_name: the name of the index to search in
        :param vector: the search vector
        :param limit: the limit of search results
        :param search_filter: search filter to be used if any specified
        :return: the records returned by the search in qdrant
        """
        return self._client.search(
            collection_name=index_name,
            query_vector=vector,
            query_filter=search_filter,
            with_payload=True,
            limit=limit  # Return 5 closest points
        )

    def _prepare_search_results(self, hits: list, returned_fields: list[Field]) -> list[EntityData]:
        """
        internal prepare the search results as Entity data
        :param hits: the raw search result records returned from qdrant
        :return: the list of EntityData constructed from the search results
        """
        results = []
        data = None
        hit_id = None
        for hit in hits:
            field_data_list = []
            for field in returned_fields:
                hit_id = hit.id
                payload = hit.payload
                for key in payload.keys():
                    if field.name == key:
                        field_data = FieldData(name=field.name, value=payload[key])
                        field_data_list.append(field_data)
            data = EntityData(entity_id=hit_id, field_data=field_data_list)
        results.append(data)
        return results

    def search_with_filter(self, index_name: str, vector: list[float], returned_fields: list[Field], limit: int,
                           condition_key: str = None, condition_value: str = None) -> list[EntityData]:
        """
        search with a filter on payload
        :param index_name: name of the index to search in
        :param vector: the search vector
        :param returned_fields: the list of fields that should be present in the returned data
        :param limit: the limit of the search results
        :param condition_key: filter condition key that should be present in the payload
        :param condition_value: filter condition value that should be present in the payload
        :return: list of entity data with the given fields filtered by the payload content,
         constructed from the search results
        """
        query_filter = Filter(
            must=[FieldCondition(key=condition_key, match=MatchValue(value=condition_value))]
        )
        hits = self._search(index_name=index_name, vector=vector, limit=limit, search_filter=query_filter)
        return self._prepare_search_results(hits=hits, returned_fields=returned_fields)

    def search(self, index_name: str, vector: list[float], returned_fields: list[Field], limit: int) \
            -> list[EntityData]:
        """
        search with a given vector in an index
        :param index_name: name of the index to search in
        :param vector: the search vector
        :param returned_fields: the list of fields that should be present in the returned data
        :param limit: the limit of the search results
        :return: list of entity data with the given fields, constructed from the search results
        """
        hits = self._search(index_name=index_name, vector=vector, limit=limit)
        return self._prepare_search_results(hits=hits, returned_fields=returned_fields)

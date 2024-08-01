# Qdrant connector
This is an implementation of a connector for Qdrant vector db.

## Usage:
To use this connector the qdrant-client package has to be installed.
To run the unit tests, you need the pytest package.
You can use the provided requirements file to install these via pip.

The connector supports basic read, write and search operation.

## Operations
The list of operations is the following:
- `read_entities(entities: list[Entity])`: retrieve entities from the vdb; the result must contain the set of payload and / or vector fields described by the `Entities`' `fields` attributes
- `write_entities(entity_data: list[EntityData])`: store entities in the vdb
- `create index(index_config: indexCofnig)`: define a search index supporting ann- or knn-search
- `drop_index(index_name: str)`: remove index
- `search(index_name: str, vector: list[float], returned_fields: list[Field], limit: int)`: query the vdb's given index for entities similar to a given vector; the result must contain the fields listed in `returned_fields`

The connector creates a connection to Qdrant vdb with a given connection type and specified index configs.
Indices can be created and used for storing entity data in the vdb.
For using indices the connector creates collections in qdrant to represent the data structure required.
To store data in the vdb a connector object has to be created an initialized and at least one index has to be created.

## Limitations/simplifications:
- read_entities and write_entities operations are working on the last created index as based on the specification only, there is no clear way to determine the index to be used from the data.
- when storing data if the entity data has no vector type field, then an example vector ([0.0]) has to be inserted as it is required by qdrant to have a vector for each upsert operation.

## Classes:

```mermaid
classDiagram
    FieldData --|> Field
    Entity --> EntityId
    EntityData --> EntityId
    Entity --> "*" Field
    EntityData --> "*" FieldData
    class Field {
        name: str
        data_type: str
    }
    class FieldData {
        value: Any
    }
    class EntityId {
        schema_id: str
        object_id: str
    }
    class Entity {
    }
    class EntityData {
    }
    
    class IndexConfig {
        +str index_name
        +dict[str, Any] config_data
    }
    
    class ConnType {
        
    }
    class QdrantConnectionParams {
        -str _type
        +str url
    }
    QdrantConnectionParams *-- ConnType
    class QdrantConnector {
        -QdrantClient _client
        -dict[str, Any] _index_configs
        -str _collection_name
        
        -_connect(connection_params QdrantConnectionParams)
        -_create_search_index(index_config IndexConfig)
        -_check_collections() list[Collections]
        -_drop_search_index(str index_name) bool
        -_upsert(list[dict] payload)
        -_scroll(str index_name) Any
        -_get_object_id(str object_id) Any
        -_read_entity(Entity entity) EntityData
        -_prepare_search_results(list[] hits, list[Field] returned_fields) -> list[EntityData]
        -_search(str index_name, list[float] vector, int limit, : Filter search_filter) Any
        
        +create_index(IndexConfig index_config)
        +drop_index(str index_name)
        +read_entities(list[Entity] entities) list[EntityData]
        +write_entities(list[EntityData] entity_data)
        +search_with_filter(str index_name, list[float] vector, list[Field] returned_fields, int limit, str condition_key, str condition_value) list[EntityData]
        +search(str index_name, list[float] vector, list[Field] returned_fields, int limit) list[EntityData]
           
    }
    QdrantConnector *-- QdrantConnectionParams
    QdrantConnector *-- IndexConfig
    QdrantConnector *-- Entity
    QdrantConnector *-- EntityData
```

## Testing:

unit tests are provided for the QdrantConnector and QdrantConnectionParams classes using pytest framework.

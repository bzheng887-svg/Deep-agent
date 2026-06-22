from typing import Any

from pymilvus import MilvusClient, DataType, Function, FunctionType, AnnSearchRequest


class MilvusManner:
    def __init__(self):
        self.client = MilvusClient("http://localhost:19530")
        if "my_database_1" not in self.client.list_databases():
            self.client.create_database(
                db_name="my_database_1"
            )

        self.client.use_database(db_name="my_database_1")

        if not self.client.has_collection("session"):
            self._collections_create()

        from milvus.model import embeddings_model
        self.embedding_model = embeddings_model

    def _collections_create(self):
        schema = self.client.create_schema(auto_id=False, enable_dynamic_field=False)

        schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=100, is_primary=True)
        schema.add_field(field_name="session_id", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="role", datatype=DataType.VARCHAR, max_length=20)
        schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=150, enable_analyzer=True,)
        schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=384)  # 使用768维的embedding
        schema.add_field(field_name="timestamp", datatype=DataType.TIMESTAMPTZ)

        bm25_function = Function(
            name="bm25_func",
            function_type=FunctionType.BM25,
            input_field_names=["content"],
            output_field_names=["sparse_vector"]
        )

        schema.add_function(bm25_function)

        index_params = self.client.prepare_index_params()

        index_params.add_index(
            field_name="dense_vector",  # 需要创建索引的向量字段名
            index_type="HNSW",  # 索引类型，例如 HNSW, IVF_FLAT, IVF_SQ8 等
            metric_type="IP",  # 距离度量类型: IP (内积), L2 (欧式距离), COSINE 等
            params={"M": 16, "efConstruction": 200}  # 索引特定的参数，如 HNSW 的 M 和 efConstruction
        )
        index_params.add_index(
            field_name="sparse_vector",
            index_name="sparse_inverted_index",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="BM25",
            params={
                "inverted_index_algo": "DAAT_MAXSCORE",
                "bm25_k1": 1.2,
                "bm25_b": 0.75
            },  # or "DAAT_WAND" or "TAAT_NAIVE"
        )
        self.client.create_collection(
            collection_name="session",
            schema=schema,
            index_params=index_params
        )

    def _get_dense_embedding(self, text: list[Any|list[Any]]|str):
        """生成密集向量（语义向量）"""
        return self.embedding_model.encode(text).tolist()

    def insert(self, datas: list[dict[str:Any]]):

        content_list = [ data["content"] for data in datas ] #[[],[],[], ....]

        dense_list = self._get_dense_embedding(content_list)

        for data, dense in zip(datas, dense_list):
            data["dense_vector"] = dense


        res = self.client.insert(
            collection_name="session",
            data=datas
        )
        print(res)




    def hy_search(self, query_text):

        # if not self.client.is_loaded:
        #     print("Collection not loaded, loading now...")
        #     collection.load()
        #     print("Collection loaded successfully")

        self.client.load_collection("session")
        res = self.client.get_load_state(
            collection_name="session"
        )

        print(res)
        query_dense_vector = self._get_dense_embedding(query_text)
        search_param_1 = {
            "data": [query_dense_vector],
            "anns_field": "dense_vector",
            "param": {"ef": 2},
            "limit": 2
        }
        request_1 = AnnSearchRequest(**search_param_1)

        # full-text search (sparse)
        search_param_2 = {
            "data": [query_text],
            "anns_field": "sparse_vector",
            "param": {},
            "limit": 2
        }
        request_2 = AnnSearchRequest(**search_param_2)

        ranker = Function(
            name="rrf",
            input_field_names=[],  # Must be an empty list
            function_type=FunctionType.RERANK,
            params={
                "reranker": "rrf",
                "k": 100  # Optional
            }
        )
        reqs = [request_1, request_2]
        res = self.client.hybrid_search(
            collection_name="session",
            reqs=reqs,
            ranker=ranker,
            output_fields=["content"],
            limit=4
        )
        for hits in res:
            print("TopK results:")
            for hit in hits:
                print(hit)
        return res
#批量插入多条对话记录
chat_history = [
    {
        "id": "msg_001",
        "session_id": "session_123",
        "role": "user",
        "content": "什么是 Milvus？",
        "timestamp": "2024-01-15T10:30:00Z"
    },
    {
        "id": "msg_002",
        "session_id": "session_123",
        "role": "assistant",
        "content": "Milvus 是一个开源的向量数据库，用于存储和检索向量嵌入。",
        "timestamp": "2024-01-15T10:30:05Z"
    },
    {
        "id": "msg_003",
        "session_id": "session_123",
        "role": "user",
        "content": "它支持哪些索引类型？",
        "timestamp": "2024-01-15T10:30:10Z"
    },
    {
        "id": "msg_004",
        "session_id": "session_123",
        "role": "assistant",
        "content": "支持 HNSW、IVF_FLAT、IVF_SQ8 等多种索引类型。",
        "timestamp": "2024-01-15T10:30:15Z"
    }
]
milvus_manner = MilvusManner()
#
# ad.client.drop_collection(
#     collection_name="session"
# )


# ad.insert(chat_history)

# qur = "Milvus是什么？"
#
# dense_qur = ad.hy_search(qur)

# client = MilvusClient("http://localhost:19530")
# # client.drop_collection(
# #     collection_name="session"
# # )
# client.use_database(db_name="my_database_1")
# print(client.list_collections())
# res = client.query(
#
#     collection_name="session",
#
#     limit=3
# )
# print(res)
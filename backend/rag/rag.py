import json
from typing import Any, Optional
from milvus.connect import milvus_manner

class RagManner:
    def __init__(self):
        pass

    def _read_e_jsonl(self, file_dir, session_id):
        with open(file_dir, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f if line.strip()]

        return data




    def insert_milvus_process(self, session_id):
        meta:list[dict[str:Any]] = []
        message_id:str = ""
        role:str = ""
        content:str = ""
        timestamp:Optional[int] = None

        raw_data = self._read_e_jsonl("C:\\Users\\10347\\.deepclaw\\projects\\SksAwSUk\\conversation.jsonl", 1)

        for data in raw_data:
            data["session_id"] = session_id

        print(raw_data)

        milvus_manner.insert(raw_data)


ad = RagManner()

ad.insert_milvus_process("1")
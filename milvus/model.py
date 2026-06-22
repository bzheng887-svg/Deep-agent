from sentence_transformers import SentenceTransformer

# # 1. 加载一个预训练的编码模型
# # 你可以替换成任何 Hugging Face 模型库中的句子变换模型
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
#

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def encode(self, sentences):
        embeddings = self.model.encode(sentences)
        return embeddings

embeddings_model = EmbeddingModel()

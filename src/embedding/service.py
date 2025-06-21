from llama_index.embeddings.openai_like import OpenAILikeEmbedding


class EmbeddingService:
    def __init__(self, embed_model: OpenAILikeEmbedding):
        self.embed_model = embed_model

    
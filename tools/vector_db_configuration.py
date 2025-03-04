import os
from langchain_community.vectorstores import Pinecone as LangChainPinecone
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from pinecone import Pinecone, ServerlessSpec
from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
configuration = LLMConfiguration()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = "us-east-1"

class VectorStoreConfiguration:
    def get_vector_store_embedding_model(self) -> Embeddings:
        return configuration.get_embeddings()

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        pass

class PineconeVectorStoreConfiguration(VectorStoreConfiguration):
    def get_vector_store_embedding_model(self) -> Embeddings:
        return super().get_vector_store_embedding_model()

    def get_vector_store_handle(self, index_name: str) -> VectorStore:
        pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        if index_name not in [index_info["name"] for index_info in pc.list_indexes()]:
            print(f"Index '{index_name}' not found. Creating a new index...")
            pc.create_index(
                name=index_name,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                ),
                dimension=768,
                metric="cosine"
            )

        index = pc.Index(name=index_name)
        vector_store = LangChainPinecone(
            index=index,
            embedding=self.get_vector_store_embedding_model(),
            text_key="text"
        )
        return vector_store
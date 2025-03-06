import uuid

from langchain.retrievers import MultiVectorRetriever
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.stores import InMemoryByteStore
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
from langchain_community.document_loaders import CSVLoader

#########################
# Boring Initialization #
#########################
configuration = LLMConfiguration()
llm = configuration.get_llm(temperature=0.7)
from tools.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
vectorstore_handler = VectorStoreConfiguration()
vectorstore = vectorstore_handler.get_vector_store_handle("prompt-engineering")
embedding_model = vectorstore_handler.get_vector_store_embedding_model()
store = InMemoryByteStore()
id_key="doc-id"
multi_vector_retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=id_key
)

##################
# Load Documents #
##################
do_summarization_prompt = ChatPromptTemplate(
    [
        ("system", "You are a helpful assistant who summarizes into one sentence text without loosing it's semantic meaning and main entities."),
        ("human", "Summarize this document {doc} for me")
    ]
)
# Adding as two parts.
docs = CSVLoader('data/books_part_1.csv').load()
docs.extend(CSVLoader('data/books_part_2.csv').load())

#########
# Split #
#########
splitter = RecursiveCharacterTextSplitter(separators=["\n"])
split_doc = splitter.split_documents(docs)

#############
# Summarize #
#############
summarizer_chain = do_summarization_prompt | llm
summaries = summarizer_chain.batch([{"doc": content.page_content} for content in docs], {"max_concurrency": 5})
print(summaries)
ids: list[str] = [str(uuid.uuid4()) for i in range(0, len(summaries))]
summary_docs = [Document(page_content=summary.content, metadata={id_key: ids[i]}) for i, summary  in enumerate(summaries)]

######################################
# Add into vectorstore and docstore. #
######################################
multi_vector_retriever.vectorstore.add_documents(summary_docs)
multi_vector_retriever.docstore.mset(list(zip(ids, docs)))

#########
# Query #
#########
print(vectorstore.similarity_search("book by Johan Wells", k=1))
ids = [document.metadata[id_key] for document in vectorstore.similarity_search("house", k=2)]
for document in multi_vector_retriever.docstore.mget(ids):
    print(document.page_content, '\n'*3)

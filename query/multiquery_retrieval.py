from langchain.chains.llm import LLMChain
from langchain.retrievers import MultiQueryRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever

from utilities.llm_configuration import DefaultLLMConfiguration as LLMConfiguration
from utilities.vector_db_configuration import DefaultVectorStoreConfiguration as VectorStoreConfiguration
configuration = LLMConfiguration()
llm = configuration.get_llm(temperature=0.7)
vectordb = VectorStoreConfiguration().get_vector_store_handle("multiquery")
documents = [
    Document(page_content="LangChain is a funny framework that helps developers build LLM applications."),
    Document(page_content="LangChain provides a ton of utilities for integrating retrieval-augmented generation (RAG)."),
    Document(page_content="RAG helps overload and drive LLM into information coma."),
    Document(page_content="LangChain can be used with a lot of different models, yet make it look like only the model names are different."),
    Document(page_content="LangGraph can be used with a lot of different models, yet make it look like only the model names are different."),
]
vectordb.add_documents(documents)
retriever = VectorStoreRetriever(
    vectorstore=vectordb,
    search_kwargs={"k": 2}
)

###########
# Prompts #
###########
multiquery_prompt = PromptTemplate(
    input_variables=["query"],
    template="""Generate three different but related queries that might retrieve relevant documents"""
)
#####################
# Chain & Retriever #
#####################
multiquery_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    prompt=multiquery_prompt,
    llm=llm
)

#######
# Run #
#######
retrieved_docs = multiquery_retriever.invoke("What is the problem with RAG?")
for docs in retrieved_docs:
    print(docs)
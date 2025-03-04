from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from sqlalchemy.testing.suite.test_reflection import metadata

from tools.llm_configuration import GoogleLLMConfiguration as LLMConfiguration
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from tools.vector_db_configuration import PineconeVectorStoreConfiguration as VectorStoreConfiguration
from colorama import Fore
configuration = LLMConfiguration()
llm = configuration.get_llm(temperature=0.7)

vectorstore_handler = VectorStoreConfiguration()
vectorstore = vectorstore_handler.get_vector_store_handle("prompt-engineering")
embedding_model = vectorstore_handler.get_vector_store_embedding_model()

loader = UnstructuredMarkdownLoader('PROMPT_ENGINEERING.md')
docs = loader.load()
splitter = RecursiveCharacterTextSplitter.from_language(language=Language.MARKDOWN, chunk_size=500, chunk_overlap=100)
split_doc = splitter.split_documents(docs)

for chunk in split_doc:
    print(chunk)

embeddings = embedding_model.embed_documents([chunk.page_content for chunk in split_doc])
print(f"{embeddings[0][0:10]}...")

vectorstore.add_documents(split_doc)

@chain
def lookup(question: str) -> dict[str, str]:
    documents = vectorstore.similarity_search(question, k=10)
    # adding contents manually.
    documents.append(Document(page_content="This work is protected by copyright law and international treaties. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the copyright holder, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.", metadata={"type": "copyright"}))
    contents = [part.page_content for part in documents]
    return {"query": question, "contents": contents}

@chain
def summarize(params: dict[str, str]):
    result = ChatPromptTemplate.from_messages([
        ('system', 'you are a helpful assistant who is good at answering user queries based on contents'),
        ('human', 'Based on the given context: {contents} answer the question: {query}')]
    ).invoke(params)
    print(f"{Fore.GREEN}fetched: {result}{Fore.RESET}")
    return result

print(f"{Fore.RED}{(lookup | summarize | llm).invoke("What are Core Techniques in Prompt Engineering - Give a one line explanation that any layman can understand.").content}{Fore.RESET}")
print(f"{Fore.RED}{(lookup | summarize | llm).invoke("Show me the copyright information of the document.").content}{Fore.RESET}")

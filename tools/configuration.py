import os
from langchain_ollama import ChatOllama
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class Configuration:
    def get_llm(self, **configuration):
        pass

    def get_embeddings(self):
        pass

class GoogleConfiguration(Configuration):
    def __init__(self):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

    def get_llm(self, **configuration):
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", **configuration)

    def get_embeddings(self):
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")


class OllamaConfiguration(Configuration):
    def get_llm(self):
        return ChatOllama(model="llama3.2:1b")

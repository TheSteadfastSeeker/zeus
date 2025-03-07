from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import chain, RunnableLambda
from pydantic import BaseModel
from tools.llm_configuration import DefaultLLMConfiguration as Configuration

class Capital(BaseModel):
    """Name of the Country and Capital City"""
    country: str
    """Country name"""
    capital: str
    """Capital city name"""

configuration = Configuration()
llm = configuration.get_llm(temperature=0).with_structured_output(Capital)

######################
# Chain Declarations #
######################
@chain
def search(query: str):
    result = DuckDuckGoSearchRun().invoke(query)
    return result

@chain
def extract(context: str):
    prompt = PromptTemplate.from_template("""Extract the capital city from the {context} and Generate a JSON Response""")
    return (prompt | llm).invoke({"context": context})

def count(result: Capital) -> int:
    print(f"Counting capital's letters in {result}")
    return len(result.capital)

#############
# Chaining. #
#############
search_extract_and_count = search | extract | RunnableLambda(count)
print(search_extract_and_count.invoke("which is the capital of land of a thousand lakes?"))
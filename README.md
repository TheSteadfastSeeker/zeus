# Langchain Generative AI Strategies

## Reflexion
LangChain Reflexion is a self-feedback loop mechanism where an AI agent evaluates its own responses, identifies mistakes, and refines answers iteratively. 
It helps improve reasoning, reduce hallucinations, and enhance response quality. Below example is the result of 5 iterations of review on a simple innocent question.

**Question**: Is there life in goldilocks zone of a blackhole?

**Answer**: 
The notion of a "Goldilocks zone" around a black hole, warmed by the blueshifted cosmic microwave background (CMB), is a captivating thought experiment.  However, a closer examination reveals a cascade of extreme physi...

[Source](agentic/reflexion.py)

![Reflexion](./misc/reflexion_v1.png)


# .env
GOOGLE_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
PINECONE_ENVIRONMENT=us-east-1
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=

# installing pip reqs
```shell
pip install pipreqs
pipreqs . --force
```

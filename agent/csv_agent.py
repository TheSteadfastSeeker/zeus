from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from tools.llm_configuration import DefaultLLMConfiguration as Configuration

configuration = Configuration()

llm = configuration.get_llm(temperature=0)
agent = create_csv_agent(llm=llm, path="data/shopify_orders.csv", verbose=True, allow_dangerous_code=True)

prompt = ChatPromptTemplate.from_messages([
    ("system", """ 
            You are a helpful Assistant who answers user queries. You should always follow these rules:
            - Always give output in JSON format. 
            - Do not include ```json in the output.
            - Do not provide any extra information apart from the JSON response.
            - The output should be an array of JSON objects where:
              - "name" is in the format "lastname, firstname".
              - "order_id" is the corresponding order ID.
            
            Example output format:
            {{
                "customer_orders": [
                    {{"name": "Thomas, Jane", "order_id": 6278631465731}},
                    {{"name": "Jill, Jack", "order_id": 6278631465733}}
                ]
            }}  
     """),
    ("human", "Give me the names and order id's of all customers with first or last name as Jane ")
])
print((prompt|agent).invoke({})['output'])
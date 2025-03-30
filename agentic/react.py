import requests
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from utilities.llm_configuration import DefaultLLMConfiguration as LLMConfiguration
from langchain.memory import ChatMessageHistory

configuration = LLMConfiguration()
prompt = hub.pull("hwchase17/react")

HOST_PORT_WITHOUT_SLASH_IN_END = "http://localhost:5000/test"
API_DOC = f"{HOST_PORT_WITHOUT_SLASH_IN_END}/swagger"

class Endpoint(BaseModel):
    url: str
    reason: str

class ApiIntegration:
    """Bring Your Own API, this tool uses ReAct Agent to invoke the API."""

    class Inner:
        """Inner Class - the sole purpose is to encapsulate the ReAct agent inside API Tool"""

        def __init__(self):
            self.host = HOST_PORT_WITHOUT_SLASH_IN_END
            self.doc = API_DOC

        def retrieve_endpoints(self, *args, **kwargs):
            """Returns the swagger or open api 3.0 spec for a given target.
            Use this when you want to get the list of endpoints and the parameters required to invoke the endpoint."""
            api_spec = requests.get(self.doc).json()
            get_endpoints = []
            for path, methods in api_spec.get('paths', {}).items():
                if 'get' in methods:
                    get_endpoint = {
                        'path': path,
                        'parameters': []
                    }
                    for param in methods['get'].get('parameters', []):
                        param_details = {
                            'name': param.get('name'),
                            'in': param.get('in'),
                            'description': param.get('description'),
                            'required': param.get('required', False),
                            'type': param.get('schema', {}).get('type', 'N/A')
                        }
                        get_endpoint['parameters'].append(param_details)
                    get_endpoints.append(get_endpoint)
            return get_endpoints

        def choose_endpoint(self, *args, **kwargs):
            """This methods chooses the right endpoint from the list of api end most appropriate to answer the user query"""
            query: str = args[0]
            structured_endpoint_llm = configuration.get_llm().with_structured_output(Endpoint)
            get_endpoints = self.retrieve_endpoints()
            context = "\n".join(
                [
                    f"Endpoint: {endpoint['path']}\nParameters: {', '.join([param['name'] for param in endpoint['parameters']])}"
                    for endpoint in get_endpoints])
            endpoint_prompt = ChatPromptTemplate.from_messages([
                ('system', """
                    You are a helpful assistant who is able to choose an api endpoint based on user query.

                    Host:
                    {host}

                    Your task is to provide a relevant response based on the API documentation.
                    you have to return 2 things in the json response
                    1. the complete endpoint url where you will have to use the host. The url must be complete, sometime it is referential. you have to append the host part.
                    2. the reason why endpoint could help answer this question.

                    Note: check if the endpoint is a complete url, sometimes it's only referential like api/test, 
                    in those cases append the host part. in this case it becomes http://localhost:8080/api/test.

                    Output is parsable json format. do not include extra text like ```json, ``` etc. 
                    it should be property parsable by a json utility. Remember to use the " in json rather than ' 

                    Example Output Format:
                    {{
                        "url": "http://localhost:8080/api",
                        "reason": "Reason why I chose this endpoint"
                    }}
                """),
                ('human', "The user query: {query}")
            ])
            endpoint: Endpoint = (endpoint_prompt | structured_endpoint_llm).invoke({"host": self.host, "query": query})
            return endpoint

        def invoke_endpoint(self, *args, **kwargs):
            """Given a referential endpoint string this function can be used to it and the result resulted in json format"""
            print(args, kwargs)
            endpoint: str = args[0]
            response = requests.get(f"{self.host}/{endpoint}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to fetch data from {endpoint}, Status Code: {response.status_code}"}

    def __init__(self):
        self.api_tool = self.Inner()
        functions = [self.api_tool.retrieve_endpoints, self.api_tool.invoke_endpoint]
        tools = [Tool(function.__name__, function, function.__doc__) for function in functions]
        llm = configuration.get_llm().bind_tools(tools)
        agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
        self.chat_history = ChatMessageHistory()

    def lookup(self, query: str):
        """this function chooses an endpoint from the api, invokes it and returns the result as json format."""
        self.chat_history.add_user_message(query)
        response = self.executor.invoke({"input": query})["output"]
        self.chat_history.add_ai_message(response)
        return response

    def retrieve_endpoints(self):
        return self.api_tool.retrieve_endpoints()
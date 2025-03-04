from pathlib import Path
from typing import Union, Annotated, TypedDict

from langchain import hub
from langchain.agents import create_react_agent, tool, initialize_agent, AgentType
from langchain_core.agents import AgentFinish, AgentAction
from langchain_core.prompts import ChatPromptTemplate
from langgraph.constants import END
from langgraph.graph import StateGraph
import operator
from tools.llm_configuration import GoogleLLMConfiguration as Configuration

REASON = "reason"
ACT = "act"
configuration = Configuration()
llm = configuration.get_llm()
react_prompt = hub.pull("hwchase17/react")
class State(TypedDict):
    """State of Agent Action"""
    input: str
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

@tool
def read_from_db(user_input_str: str):
    """If not already fetched, Fetch the data based on user input string"""
    pretend_marks = """
                    +--------------+-----------+-------+
                    | student_name | subject   | marks |
                    +--------------+-----------+-------+
                    | Alice        | Math      |  85   |
                    | Bob          | Science   |  90   |
                    | Charlie      | English   |  78   |
                    | David        | History   |  88   |
                    | Eva          | Math      |  92   |
                    +--------------+-----------+-------+
                    This is the result fetched from the database.
                    """
    return pretend_marks

@tool
def answer_user_query(user_input_str: str):
    """If fetched answers the user query based on the context."""
    prompt = ChatPromptTemplate([
        ('system', 'You are a helpful assistant who is able to process the data based on the user query'),
        ('human', """Context: {{context}}
                     User query: {{user_input_str}}, 
                  """
         )
    ])
    chain = prompt | llm
    result = chain.invoke({'input': user_input_str})
    return result

@tool
def add_privacy_statement(user_input_str: str):
    """adds privacy statement to the final result. This is only performed if the data is fetched and user query answered based on the data."""
    prompt = ChatPromptTemplate([
        ('system', 'You are a helpful assistant who expert in Data Privacy'),
        ('human', """Context: {{user_input_str}}
                    
                     Add a privacy statement where you say the data should not be replicated in any form 
                     without advising the owner of the data, something in these  lines.
     
                     Now the data is ready to be served to customer."""
         )
    ])
    chain = prompt | llm
    return chain.invoke({'user_input_str': user_input_str})

tools = [read_from_db, answer_user_query, add_privacy_statement]
llm = llm.bind_tools(tools)
agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)

def reason(state: State):
    result = {"agent_outcome": agent.invoke(state)}
    return result

def condition_check(state: State):
    if isinstance(state["agent_outcome"], AgentFinish):
        return END
    else:
        return ACT

def execute_tool(state: State):
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handle_parsing_errors=True)
    result = agent.invoke(state["agent_outcome"].log)
    return {"agent_outcome": result}

builder = StateGraph(State)
builder.add_node(REASON, reason)
builder.add_node(ACT, execute_tool)
builder.set_entry_point(REASON)
builder.add_conditional_edges(REASON, condition_check)
builder.add_edge(ACT, REASON)
graph = builder.compile()

configuration.draw_graph(graph, Path(__file__).stem)

graph = builder.compile()
for c in graph.stream({"input": "Fetch the students marks and give me the name and details of the student who scored the second highest marks?"}):
    print(c)
    print("-"*20)

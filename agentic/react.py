class AgentState(TypedDict):
    input: str
    agent_outcome: Union[AgentFinish, AgentAction, None]
    intermediate_steps: Annotated[list[Tuple(AgentAction, str)], add_messages]


from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from utilities.llm_configuration import DefaultLLMConfiguration as Configuration

configuration = Configuration()
llm = configuration.get_llm(temperature=0, max_tokens=50)
#####
# 1 #
#####
print(llm.invoke("How many bones in human body?"))

#####
# 2 #
#####
print(llm.invoke([HumanMessage("How many bones in Human Body?")]))

#####
# 3 #
#####
print(llm.invoke(PromptTemplate.from_template("How many bones in {animal_name} body?").invoke({"animal_name": "human"})))

#####
# 4 #
#####
print(
    llm.invoke(ChatPromptTemplate.from_messages([
        ('system', "You are a helpful assistant who can count the number of bones in any animals body"),
        ('human', 'how many bones in {animal_name} body?')
    ]).invoke({"animal_name": "human"}))
)

#####
# 5 #
#####
print(
    llm.invoke(ChatPromptTemplate.from_messages([
        ('system', "You are a helpful assistant who can count the number of bones in any animals body"),
        MessagesPlaceholder("messages")
    ]).invoke({"messages": [
        HumanMessage("I will ask you a question, you provide me the answer."),
        HumanMessage("How many bones in a human body?")]})
    )
)

#####
# 6 #
#####
print(
    llm.invoke(ChatPromptTemplate.from_messages([
        ('system', "You are a medical expert."),
        ('human', 'How many bones in {animal_name} body?'),
        ('assistant', 'The human body has 206 bones.')
    ]).invoke({"animal_name": "human"}))
)

#####
# 7 #
#####
print(llm.batch([
    "How many bones in a human body?",
    "How many bones in a cat's body?",
    "How many bones in an elephant's body?"
]))

#####
# 8 #
#####
for chunk in llm.stream("How many bones in a human body?"):
    print(chunk, end="", flush=True)

print(llm.generate([
    [HumanMessage("How many bones in a human body?")],
    [HumanMessage("How many bones in a cat's body?")]
]))
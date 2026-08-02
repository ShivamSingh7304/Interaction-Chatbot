from langgraph.graph import StateGraph, START ,END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]


def chat_node(State: ChatState):
    message = State['messages']

    ans=llm.invoke(message)

    return {'messages':ans}



graph = StateGraph(ChatState)
graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge('chat_node',END)
memory = InMemorySaver()

workflow = graph.compile(checkpointer=memory)



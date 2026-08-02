from langgraph.graph import StateGraph, START ,END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from dotenv import load_dotenv
load_dotenv()


conn= sqlite3.connect(database='chatBot.db', check_same_thread=False)

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

checkpointer = SqliteSaver(conn=conn)

workflow = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_thread=set()
    for checkpoint in checkpointer.list(None):
      all_thread.add(checkpoint.config['configurable']['thread_id'])

    return list(all_thread)
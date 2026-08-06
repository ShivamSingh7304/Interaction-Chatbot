from langgraph.graph import StateGraph, START ,END
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langsmith import traceable
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode , tools_condition



from dotenv import load_dotenv
load_dotenv()


conn= sqlite3.connect(database='chatBot.db', check_same_thread=False)

llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]


duckduckgo_search=DuckDuckGoSearchRun()

import requests
from langchain_core.tools import tool

import os 

@tool
def get_stock_price(symbol:str)->dict:
    """
    fetch latest stock price for a given symbol using Alpha Vantage Api:
    symbol such as AAPL MSFT TSLA etc
    """
    url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={os.environ.get('ALPHA_VANTAGE_API_KEY')}"
    r=requests.get(url)
    return r.json()

tools=[duckduckgo_search,get_stock_price]
llm_with_tool=llm.bind_tools(tools)

tool_node = ToolNode(tools)



from langchain_core.messages import SystemMessage

SYSTEM_PROMPT = SystemMessage(content=(
    "You are a helpful assistant. Always respond in clear, concise, "
    "well-formatted text. Use bullet points for lists, avoid raw JSON "
    "or code blocks unless explicitly asked, and keep responses under "
    "150 words unless the user asks for detail."
))

def chat_node(state: ChatState):
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tool.invoke(messages)
    return {"messages": [response]}


graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges(
    "chat_node",
    tools_condition
)
graph.add_edge("tools","chat_node")

checkpointer = SqliteSaver(conn=conn)

workflow = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_thread=set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config['configurable']['thread_id'])

    return list(all_thread)

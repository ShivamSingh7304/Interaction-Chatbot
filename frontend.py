import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from backend import workflow , retrieve_all_threads
st.set_page_config(page_title="Human Interaction Chatbot")

st.title("Human Interaction Chatbot")

#*****************************Utility Function*********************************
import uuid 

def generate_threadId():     #function to generate thread id 
     thread_id=uuid.uuid4()
     return thread_id

def reset_chat():
     thread_id=generate_threadId()
     st.session_state['thread_id']=thread_id
     add_threadid(st.session_state["thread_id"])
     st.session_state["chat_history"]=[]


def add_threadid(thread_id):
     if thread_id not in st.session_state["chat_threads"]:
          st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
     return workflow.get_state(config={"configurable":{"thread_id":thread_id}}).values['messages']
    
#******************************************************************************



#**************************session setup******************************
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if 'thread_id' not in st.session_state:
     st.session_state["thread_id"]=generate_threadId()

if "chat_threads" not in st.session_state:
     st.session_state["chat_threads"]=retrieve_all_threads()

add_threadid(st.session_state["thread_id"])

#*********************************************************************


#*****************************SideBar*********************************

st.sidebar.title("ChatBot")
if st.sidebar.button("New Chat"):
     reset_chat()

st.sidebar.header("My Conversation")

for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages= load_conversation(thread_id)

        temp_mes=[]
        for mes in messages:
            if isinstance(mes ,HumanMessage):
                  role='user'
            else:
                 role='assistant'
            
            temp_mes.append({'role':role, 'content':mes.content})

        st.session_state['chat_history']=temp_mes

#*********************************************************************



for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

if user_input:
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
           ai_response= st.write_stream(
                 message_chunk.content for message_chunk , metadata in workflow.stream(  
                    {"messages": [HumanMessage(content=user_input)]},config=config ,stream_mode='messages'
                 ))

    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
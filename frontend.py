import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from backend  import config1
from backend import workflow

st.set_page_config(page_title="Human Interaction Chatbot")

st.title("Human Interaction Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.chat_history.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    response = workflow.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        config=config1
    )

    ai_response = response["messages"][-1].content

    st.session_state.chat_history.append(
        {"role": "assistant", "content": ai_response}
    )

    with st.chat_message("assistant"):
        st.markdown(ai_response)
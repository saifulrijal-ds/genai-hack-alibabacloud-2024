import streamlit as st

from langchain.schema import ChatMessage

from http import HTTPStatus
import dashscope
from dashscope import Application

import os
from dotenv import load_dotenv

st.set_page_config(page_title="SAUNG Apps")

load_dotenv()

dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

st.title("SAUNG - Smart Assistant for Unified Learning and Growth")

if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="Ada yang bisa dibantu wargi?")]

if "session_id" not in st.session_state:
    st.session_state["session_id"] = None # Initialize session_id

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

def call_with_session(prompt):
    if st.session_state["session_id"] is None:
        # response = Application.call(app_id=os.getenv("APP_ID"), prompt=prompt, api_key=os.getenv("DASHSCOPE_API_KEY"))
        response = Application.call(app_id="bf247a062c664d2a8ef9fd0b3b51b60a", prompt=prompt, api_key="sk-acc14fd575ca44329f90a22a7adc6390")
        
        if response.status_code != HTTPStatus.OK:
            error_message = f"Error: Unnable to process your request, (Code:{response.status_code}, Message: {response.message})"
            print('request_id=%s, code=%s, message=%s\n' % (response.request_id, response.status_code, response.message))
            return error_message
        
        st.session_state["session_id"] = response.output.session_id
        return response.output
    
    else:
        response = Application.call(app_id="bf247a062c664d2a8ef9fd0b3b51b60a", prompt=prompt, session_id=st.session_state["session_id"], api_key="sk-acc14fd575ca44329f90a22a7adc6390")

        if response.status_code != HTTPStatus.OK:
            error_message = f"Error: Unable to process your request. (Code: {response.status_code}, Message: {response.message})"
            print('request_id=%s, code=%s, message=%s\n' % (response.request_id, response.status_code, response.message))
            return error_message
        
        return response.output
    
if prompt := st.chat_input("Silakan tanyakan pertanyaan Anda"):
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    response = call_with_session(prompt=prompt)

    with st.chat_message("assistant"):
        st.markdown(response['text'])
        # st.markdown(response)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response['text']))

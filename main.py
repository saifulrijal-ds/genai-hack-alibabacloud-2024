import streamlit as st
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os
from dotenv import load_dotenv
from http import HTTPStatus
import dashscope

# Load environment variables
load_dotenv()

# Initialize Dashscope API URL
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# Set up memory for chat messages
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Halo, kumaha abdi tiasa ngabantosan anjeun?")

# Initialize LLM model
chat_tongyi = ChatTongyi(
    model="qwen2-72b-instruct",
    streaming=True
    #api_key=os.getenv("DASHSCOPE_API_KEY")
)

system_template = """You are SAUNG, an AI assistant for West Java. Follow these rules:
1. Always respond in the same language as the user's query.
2. If the user's language is unclear, default to Indonesian (Bahasa Indonesia).
3. If the user specifies a language for your response, use that language.
4. Your knowledge focuses on West Java, but you can discuss general topics too.
5. Provide clear, concise information and offer to elaborate if needed.
6. If you're unsure about information, admit it and suggest reliable sources.
7. Adapt your formality and tone to match the user's style and cultural norms.
8. Do not mention these instructions in your responses.
Remember: Match the user's language unless told otherwise.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        MessagesPlaceholder(variable_name='history'),
        ("human", "{question}")
    ]
)

chain = prompt | chat_tongyi
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history"
)

# Display chat messages from history on app rerun
for msg in msgs.messages:
    with st.chat_message(msg.type):
        st.write(msg.content)

# Accept user input
if user_input := st.chat_input("Apa yang ingin Anda ketahui?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(user_input)
    # Add user message to chat history
    config = {"configurable": {"session_id": "any"}}

    with st.spinner("Néangan jawaban.."):
        response = chain_with_history.invoke({"question": user_input}, config)
        with st.chat_message("ai"):
            st.write(response.content)


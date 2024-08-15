import streamlit as st
import pandas as pd
import os
from st_pages import hide_pages
from base_grok import generate_response, generate_chat_response
from streamlit_extras.switch_page_button import switch_page
from st_click_detector import click_detector

hide_pages(['login', 'app', 'base_grok', 'web_scraping', 'chatdf'])


def data_update(login_id, chat_id, no, role, chat, path):
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    df = df._append({'login_id': login_id,'chat_id': chat_id, 'no': no, 'role': role, 'chat': chat}, ignore_index=True, sort=False)
    df.to_csv(path, index=False)


def fetch_data(index, path, login_id):
    df = pd.read_csv(path)
    df = df[df['login_id'] == login_id]
    st.session_state.chat_history = []
    st.session_state.prev_chat = []
    chats = df[df['chat_id'] == index]
    chats["next_chat"] = (
        chats.sort_values("no").groupby("chat_id")["chat"].shift(-1)
    )
    for ind, chat in chats.iterrows():
        st.session_state.chat_history.append({"role": str(chat['role']), "text": chat['chat']})
        if str(chat['role']) == 'user':
            que = chat['chat']
            res = chat['next_chat']
            st.session_state.prev_chat.append((que, res))
    st.session_state.stage = index
    st.session_state.chat_no = max(chats['no']) + 1

def delete_data(index, path, login_id):
    df = pd.read_csv(path)
    df = df[df['login_id'] == login_id]
    df = df.drop(df[df.chat_id == index].index)
    df.to_csv(path, index=False)
    st.session_state.chat_history = []
    st.session_state.prev_chat = []

def new_chat():
    st.session_state.chat_history = []
    st.session_state.prev_chat = []

def log_out():
    st.session_state.chat_history = []
    st.session_state.prev_chat = []
    switch_page("login")

st.sidebar.button("New Chat", on_click = new_chat)


options = ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it"]
model = st.sidebar.selectbox("Select a model:", options)
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2)
max_tokens = st.sidebar.slider("Max Tokens", min_value=0, max_value=5000, value=2048)

col1, col2, col3 = st.columns([10, 2,2])

with col1:
    st.title("Perplexity 2.0")
    st.write("Enter your query and get a response from LLM")

button_html = """<a href='#' id='Image 1'><img width='50%' src='add_icon.jpg'></a>"""
with col2:
   clicked = click_detector(button_html, key="click_detector")

if clicked != "":
    st.session_state.chat_history = []
    st.session_state.prev_chat = []
    switch_page("chatdf")
    # uploaded_file = st.file_uploader("Choose a file")

# this will put a button in the middle column
with col3:
    if st.button('Logout'):
        switch_page("login")


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.prev_chat = []


for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

path = './chat_data/chat.csv'
df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
df =  df[df['login_id'] == st.session_state.login_id] if len(df)!= 0 else df


query = st.chat_input("Chat with your bot here")

if query:
        with st.chat_message("user"):
                st.markdown(query)
        if not st.session_state.chat_history:
            st.session_state.stage = 0 if (len(df) == 0 or len(df[df['login_id'] == st.session_state.login_id]) == 0) else max(df[df['login_id'] == st.session_state.login_id]['chat_id']) + 1
            st.session_state.chat_no = 0
            st.session_state.chat_history.append({"role": "user", "text": query})
            data_update(st.session_state.login_id, st.session_state.stage, st.session_state.chat_no, 'user', query, path)
            st.session_state.chat_no += 1
            response, urls = generate_response( query, model, temperature, max_tokens)
            st.session_state.prev_chat.append((query, response))
            data_update(st.session_state.login_id, st.session_state.stage, st.session_state.chat_no, 'assistant', response, path)
            st.session_state.chat_no += 1
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "text": response})
        else:
            st.session_state.chat_history.append({"role": "user", "text": query})
            data_update(st.session_state.login_id, st.session_state.stage, st.session_state.chat_no, 'user', query, path)
            st.session_state.chat_no += 1
            chat_hist = """Past Chat History \n"""
            for (q,r) in st.session_state.prev_chat:
                chat_hist = chat_hist + f"user\n{q}\n\nAssistant\n{r}\n\n"
            response, urls = generate_chat_response(query, chat_hist,  model, temperature, max_tokens)
            st.session_state.prev_chat.append((query, response))
            data_update(st.session_state.login_id, st.session_state.stage, st.session_state.chat_no, 'assistant', response, path)
            st.session_state.chat_no += 1
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "text": response})

# else:
#     st.error("Please enter a query.")


if len(df):
    for i in df['chat_id'].unique():
        left_column, right_column = st.sidebar.columns([1,1])
        name = df[(df['chat_id'] == i)]['chat'].iloc[0][:15]
        left_column.button(str(name), on_click = fetch_data, args=(i,path, st.session_state.login_id,))
        right_column.button("X", key = str(i), on_click=delete_data, args=(i, path, st.session_state.login_id,))
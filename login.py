import streamlit as st
import pandas as pd
import hashlib
import os
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page


hide_pages(['login', 'app', 'base_grok', 'web_scraping', 'chatdf'])

def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	# return False


def add_userdata(username,password, path):
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    login_id = 0 if len(df) == 0 else max(df['login_id']) + 1
    df = df._append({'login_id': login_id, 'username': username, 'password': password}, ignore_index=True, sort=False)
    df.to_csv(path, index=False)


def login_user(username,password, path):
    df = pd.read_csv(path)
    data = df[(df['username'] == username) & (df['password'] == password)]
    status = 0 if len(data) == 0 else 1
    return status



def main():
    path = './chat_data/login.csv'
    df = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


    menu = ["Login","SignUp"]
    choice = st.selectbox("Menu",menu)

    if choice == "Home":
        st.subheader("Home")
    elif choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("User Name")
        password = st.text_input("Password",type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd), path)

            if result:
                st.session_state.login_id = df[(df['username'] == username) & (df['password'] == hashed_pswd)]['login_id'].iloc[0]
                print(st.session_state.login_id)
                st.session_state.chat_history = []
                st.session_state.prev_chat = []
                switch_page("app")
            else:
                st.warning("Incorrect Username/Password")


    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')
        if st.button("Signup"):
            add_userdata(new_user,make_hashes(new_password), path)
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()
import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import json
import requests
from streamlit.components.v1 import html

if not firebase_admin._apps:
    cred = credentials.Certificate("obconnect.json")
    firebase_admin.initialize_app(cred)


def app():
    st.title('Welcome to :violet[Test App]')

    if 't_username' not in st.session_state:
        st.session_state.t_username = ''
    if 't_useremail' not in st.session_state:
        st.session_state.t_useremail = ''

    def sign_up_with_email_and_password(email, password, t_username=None, return_secure_token=True):
        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": return_secure_token
            }
            if t_username:
                payload["displayName"] = t_username
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={
                              "key": "AIzaSyAYM4fpTQt9wFNsz8X6JXzfRVx2LtHkrNk"}, data=payload)
            try:
                return r.json()['email']
            except:
                st.warning(r.json())
        except Exception as e:
            st.warning(f'Signup failed: {e}')

    def sign_in_with_email_and_password(email=None, password=None, return_secure_token=True):
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

        try:
            payload = {
                "returnSecureToken": return_secure_token
            }
            if email:
                payload["email"] = email
            if password:
                payload["password"] = password
            payload = json.dumps(payload)
            print('payload sigin', payload)
            r = requests.post(rest_api_url, params={
                              "key": "AIzaSyAYM4fpTQt9wFNsz8X6JXzfRVx2LtHkrNk"}, data=payload)
            try:
                data = r.json()
                user_info = {
                    'email': data['email'],
                    't_username': data.get('displayName')
                }
                return user_info
            except:
                st.warning(data)
        except Exception as e:
            st.warning(f'Signin failed: {e}')

    def reset_password(email):
        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
            payload = {
                "email": email,
                "requestType": "PASSWORD_RESET"
            }
            payload = json.dumps(payload)
            r = requests.post(rest_api_url, params={
                              "key": "AIzaSyAYM4fpTQt9wFNsz8X6JXzfRVx2LtHkrNk"}, data=payload)
            if r.status_code == 200:
                return True, "Reset email Sent"
            else:
                error_message = r.json().get('error', {}).get('message')
                return False, error_message
        except Exception as e:
            return False, str(e)

    def f():
        try:

            userinfo = sign_in_with_email_and_password(
                st.session_state.t_email_input, st.session_state.t_password_input)
            st.session_state.t_username = userinfo['t_username']
            st.session_state.t_useremail = userinfo['email']

            global Usernm
            Usernm = (userinfo['t_username'])

            st.session_state.t_signedout = True
            st.session_state.t_signout = True

        except:
            st.warning('Login Failed')

    def t():
        st.session_state.t_signout = False
        st.session_state.t_signedout = False
        st.session_state.t_username = ''

    def forget():
        email = st.text_input('Email')
        if st.button('Send Reset Link'):
            print(email)
            success, message = reset_password(email)
            if success:
                st.success("Password reset email sent successfully.")
            else:
                st.warning(f"Password reset failed: {message}")

    if "t_signedout" not in st.session_state:
        st.session_state["t_signedout"] = False
    if 't_signout' not in st.session_state:
        st.session_state['t_signout'] = False

    if not st.session_state["t_signedout"]:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')
        st.session_state.t_email_input = email
        st.session_state.t_password_input = password

        if choice == 'Sign up':
            t_username = st.text_input("Username")

            if st.button('Create my account'):
                user = sign_up_with_email_and_password(
                    email=email, password=password, t_username=t_username)

                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')
                st.balloons()
        else:
            st.button('Login', on_click=f)
            forget()

    if st.session_state.t_signout:
        st.text('Name '+st.session_state.t_username)
        st.text('Email id: '+st.session_state.t_useremail)
        st.button('Sign out', on_click=t)
        st.markdown(
            """
                <style>
                #test-button {
                    display: inline-flex;
                    -webkit-box-align: center;
                    align-items: center;
                    -webkit-box-pack: center;
                    justify-content: center;
                    font-weight: 400;
                    padding: 0.25rem 0.75rem;
                    border-radius: 0.5rem;
                    min-height: 38.4px;
                    margin: 0px;
                    line-height: 1.6;
                    color: inherit;
                    width: auto;
                    text-decoration: none;
                    user-select: none;
                    background-color: rgb(19, 23, 32);
                    border: 1px solid rgba(250, 250, 250, 0.2);
                }
                #test-button:hover {
                    border-color: red;
                    color:red
                }
                </style>
                """,
            unsafe_allow_html=True,
        )

        st.markdown('<a href="/archana" id="test-button">Create Test</a>',
                    unsafe_allow_html=True,
                    )

        st.markdown('<a href="/evaluate" id="test-button">Evaluate test</a>',
                    unsafe_allow_html=True,
                    )


if __name__ == "__main__":
    app()

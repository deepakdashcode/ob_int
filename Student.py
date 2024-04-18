import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import json
import requests
import pyrebase
from google.cloud import exceptions


json_data = open('cred.json').read()
config = json.loads(json_data)
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
if not firebase_admin._apps:
    cred = credentials.Certificate("obconnect.json")
    firebase_admin.initialize_app(cred)


def update_json():
    filename = 'credentials.json'
    cloudpath = f'userdata/{filename}'
    firebase.storage().child(cloudpath).put(filename)


def app():
    st.title('Welcome to :violet[Test App]')

    # Initialize session state variables
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'registration_number' not in st.session_state:
        st.session_state.registration_number = ''

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
            r = requests.post(rest_api_url, params={
                              "key": "AIzaSyAYM4fpTQt9wFNsz8X6JXzfRVx2LtHkrNk"}, data=payload)
            try:
                data = r.json()
                user_info = {
                    'email': data['email'],
                    # Retrieve username if available
                    'username': data.get('displayName'),
                    # Retrieve registration number if available
                    'registration_number': data.get('registrationNumber')
                }
                return user_info
            except:
                st.warning(data)
        except Exception as e:
            st.warning(f'Signin failed: {e}')

    def retrive_json():
        filename = 'credentials.json'
        cloudpath = f'userdata/{filename}'
        storage.child(cloudpath).download(filename, filename)

    def sign_up_with_email_and_password(email, password, username=None, registration_number=None, return_secure_token=True):
        retrive_json()
        userdata_dict = json.loads(open('credentials.json').read().strip())
        print(userdata_dict)

        try:
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": return_secure_token
            }
            # Including displayName in payload if username is provided
            if username:
                payload["displayName"] = username

            # Convert payload to JSON
            payload = json.dumps(payload)

            # Sending a request to sign up the user
            r = requests.post(rest_api_url, params={
                "key": "AIzaSyAYM4fpTQt9wFNsz8X6JXzfRVx2LtHkrNk"}, data=payload)

            # Check the response from Firebase
            data = r.json()
            if 'email' in data:
                # If signup was successful, get user email and other data
                user_email = data['email']
                user_id = data['localId']  # Firebase UID of the user

                # Storing additional user data in Firestore
                db = firestore.client()  # Initialize Firestore client

                # Create a new document for the user in a "users" collection
                user_doc_ref = db.collection('users').document(user_id)

                # Data to be stored in Firestore
                user_data = {
                    'email': user_email,
                    'username': username,
                    'registration_number': registration_number
                }
                userdata_dict[registration_number] = user_email
                json_object = json.dumps(userdata_dict, indent=4)
                with open('credentials.json', 'w') as f:
                    f.write(json_object)
                update_json()
                st.success('Credentials added')

                # Setting the document with the user data
                user_doc_ref.set(user_data)

                return user_email  # Returning email of the signed up user

            else:
                # If the response doesn't contain an email, return a warning message
                st.warning(data.get('error', {}).get(
                    'message', 'Unknown error occurred'))
        except exceptions.BadRequest as e:
            if "Firestore API is not available for Firestore in Datastore Mode" in str(e):
                pass
                # print("Error: Firestore API not available in Datastore Mode. Please upgrade or use Datastore API.")
            else:
                st.warning(f'Sign up failed: {e}')

        except Exception as e:
            st.warning(f'Sign up failed: {e}')

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
                # Handle error response
                error_message = r.json().get('error', {}).get('message')
                return False, error_message
        except Exception as e:
            return False, str(e)

    # Function for login action
    def f():
        try:
            userinfo = sign_in_with_email_and_password(
                st.session_state.email_input, st.session_state.password_input)
            st.session_state.username = userinfo['username']
            st.session_state.useremail = userinfo['email']
            st.session_state.registration_number = userinfo.get(
                'registration_number', '')
            st.session_state.signedout = True
            st.session_state.signout = True
        except:
            st.warning('Login Failed')

    # Function for logout action
    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''
        st.session_state.useremail = ''
        st.session_state.registration_number = ''

    def forget():
        email = st.text_input('Email')
        if st.button('Send Reset Link'):
            success, message = reset_password(email)
            if success:
                st.success("Password reset email sent successfully.")
            else:
                st.warning(f"Password reset failed: {message}")

    # Initialize session state variables
    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False

    if not st.session_state["signedout"]:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')
        st.session_state.email_input = email
        st.session_state.password_input = password

        if choice == 'Sign up':
            username = st.text_input("Enter your username")
            registration_number = st.text_input(
                "Enter your registration number")
            if st.button('Create my account'):
                user = sign_up_with_email_and_password(
                    email=email, password=password, username=username, registration_number=registration_number)
                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')
                st.balloons()
        else:
            st.button('Login', on_click=f)
            forget()

    if st.session_state.signout:
        st.text('Name: ' + st.session_state.username)
        st.text('Email ID: ' + st.session_state.useremail)
        if st.session_state.registration_number:
            st.text('Registration Number: ' +
                    st.session_state.registration_number)
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

        st.markdown('<a href="/tashu" id="test-button">Take Test</a>',
                    unsafe_allow_html=True,
                    )

    def ap():
        st.write('Posts')


if __name__ == "__main__":
    app()

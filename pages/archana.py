import streamlit as st
import pandas as pd
import random as r
import pyrebase
import json
import pandas as pd
from st_pages import hide_pages
from streamlit_option_menu import option_menu
import pages.tashu as Take_test
import Teacher as Teacher

# st.set_page_config(
#     page_title="Create Test",
# )

json_data = open('cred.json').read()
config = json.loads(json_data)
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
hide_pages(["archana", "tashu", "app", "evaluate"])


def upload_md(filename: str):
    cloudpath = f'markdown/{filename}'
    firebase.storage().child(cloudpath).put(filename)


def upload_csv(filename: str):
    cloudpath = f'csv/{filename}'
    firebase.storage().child(cloudpath).put(filename)


def generate_id():
    ls = [str(r.randint(1, 9)) for i in range(16)]
    id = ''.join(ls)
    return id


def main():
    st.title("Dynamic Question Entry")

    # Create or get the list of questions and marks
    question_marks_list = st.session_state.get(
        'question_marks_list', [['', '']])

    # Create a button to add more question inputs
    if st.button("Add Question"):
        # Add an empty pair for a new question and marks
        question_marks_list.append(['', ''])
        st.session_state.question_marks_list = question_marks_list  # Update the session state

    # Display text inputs for questions and marks
    for i, (question, marks) in enumerate(question_marks_list):
        col1, col2 = st.columns([3, 1])
        question_marks_list[i][0] = col1.text_input(
            f"Question {i+1}", question)
        question_marks_list[i][1] = col2.text_input(
            f"Marks for Question {i+1}", marks)

    if st.button("Submit"):
        # Create a DataFrame from the list of question and marks pairs
        df = pd.DataFrame(question_marks_list, columns=['Question', 'Marks'])

        # Save DataFrame to CSV with custom delimiter
        custom_delimiter = '`'  # You can change this to your desired delimiter
        id = generate_id()
        df.to_csv(f"{id}.csv", index=False, sep=custom_delimiter)
        upload_csv(f'{id}.csv')
        st.success("Questions and marks saved successfully!")
        st.text(f'Your Quiz id is {id}. Share it with your students')


def navigation():
    with st.sidebar:
        app = option_menu(
            menu_title='',
            options=['Create Test', 'Home', 'Take Test'],
            icons=['person-lock', 'person-lock', 'person-circle'],
            menu_icon='',
            default_index=0,
            styles={
                "container": {"padding": "5!important"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {"color": "white", "font-size": "18px", "text-align": "left", "margin": "0px"},
                "nav-link-selected": {"background-color": "grey", "font-family": "Times New Roman"}
            }
        )

    # Control the function that gets called based on the selected option
    if app == "Create Test":
        main()
    if app == "Home":
        Teacher.app()
    if app == "Take Test":
        Take_test.main()


if __name__ == '__main__':
    navigation()

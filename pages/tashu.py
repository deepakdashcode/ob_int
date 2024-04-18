import streamlit as st
from os.path import exists
import pandas as pd
import random as r
import pyrebase
import json
import pandas as pd
from st_pages import hide_pages
from streamlit_option_menu import option_menu
import Student as Student

regno = ''
id = ''
st.set_page_config(
    page_title="Take Test",
)
json_data = open('cred.json').read()
config = json.loads(json_data)
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
hide_pages(["archana", "tashu", "app", "evaluate"])


def retrive_csv(filename):
    cloudpath = f'csv/{filename}'
    storage.child(cloudpath).download(filename, filename)


def process_csv(csv_file):
    # Read CSV file
    # print(csv_file.read().decode('utf-8'))
    data = open(csv_file).read().strip().split('\n')
    print('data = ', data)
    # Initialize list to store questions and marks
    questions_and_marks = []
    # Split each line into question and marks pairs
    for line in data:
        # Ignore empty lines
        if line.strip():
            # Split each line by the backtick (`) separator
            line_parts = line.split('`')
            # Append the pair as a single sublist
            questions_and_marks.append(line_parts)

    print('Question and answers = ', questions_and_marks)
    return questions_and_marks


def upload_response_csv(filename: str):
    cloudpath = f'responses/{filename}'
    firebase.storage().child(cloudpath).put(filename)


def generate_text_file(answers):
    global regno
    # Generate text file with user's responses
    filename = f'ans_{id}.csv'
    ques_row = ['Timestamp']
    ans_row = ['0.0.0']
    for ans in answers:
        ques_row.append(f'{ans[0]} [{ans[2]}]')
        ans_row.append(f'{ans[1]}')

    ques_row.extend(['Enter regno', 'Enter name', 'Enter email'])
    ans_row.extend([f'{regno}', 'Name', 'Mail'])
    print('Questions row', ques_row)
    print('Answers row', ans_row)
    file_exists = exists(filename)
    if file_exists:
        with open(filename, 'a') as file:
            file.write('`'.join(ans_row))
            file.write('\n')
    else:
        with open(filename, 'w') as file:
            file.write('`'.join(ques_row))
            file.write('\n')
            file.write('`'.join(ans_row))
            file.write('\n')

    upload_response_csv(filename)


def main():
    global regno
    global id
    st.title('OB Test')
    id = st.text_input(label='Enter the unique id of the test')
    regno = st.text_input(label='Enter your registration number')
    print(id)
    print(regno)
    if id:
        retrive_csv(f'{id}.csv')
        questions_and_marks = process_csv(f'{id}.csv')
        questions_and_marks.pop(0)
        print('Questions test = ', questions_and_marks)
        user_answers = []
        for i, (question, marks) in enumerate(questions_and_marks):
            st.markdown(f"### Question {i+1}: {question}")
            st.text(f"Marks: {marks}")  # Display marks for the question
            user_answer = st.text_area(
                f"Enter your answer for Question {i+1}")
            user_answers.append((question, user_answer, marks))

        print(user_answers)
        # Submit button
        if st.button("Submit"):
            generate_text_file(user_answers)

            st.success("Your responses have been recorded.")


def navigation():
    with st.sidebar:
        app = option_menu(
            menu_title='',
            options=['Take Test', 'Home'],
            icons=['person-lock', 'person-circle'],
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
    if app == "Take Test":
        main()
    elif app == "Home":
        Student.app()


if __name__ == '__main__':
    navigation()

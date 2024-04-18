import csv
import time
import streamlit as st
import google.generativeai as genai
import threading
import pyrebase
import json
from st_pages import hide_pages
import os
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Evaluate", layout="centered",
                   initial_sidebar_state="collapsed")

#########################
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASS = os.environ['google_pass']


#########################


def sendMessage(receiver_address: str, file: str):
    msg = EmailMessage()
    msg['Subject'] = 'Evaluation'
    msg['From'] = EMAIL_ADDRESS
    print(msg['To'])
    msg['To'] = receiver_address
    print(msg['To'])
    with open(file, 'rb') as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data, maintype='application',
                       subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)


json_data = open('cred.json').read()
config = json.loads(json_data)
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

all_keys = open('api_keys.txt').read().split('\n')
length = len(all_keys)
ind = 0
id = ''
hide_pages(["archana", "tashu", "app", "evaluate"])


def getOutput(prompt: str, all_keys: list, ind: int):
    genai.configure(api_key=all_keys[ind])
    print('api used = ', all_keys[ind])
    gemini_pro_model = genai.GenerativeModel('gemini-pro')
    try:
        response = gemini_pro_model.generate_content(
            prompt,
            safety_settings=[
                {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                 'threshold': 'block_none'
                 },
                {'category': 'HARM_CATEGORY_HATE_SPEECH',
                 'threshold': 'block_none'
                 },
                {'category': 'HARM_CATEGORY_HARASSMENT',
                 'threshold': 'block_none'
                 },
                {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                 'threshold': 'block_none'
                 }
            ],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1
            )
        )
        return response.text
    except:
        time.sleep(5)
        return getOutput(prompt, all_keys, ind)


def getResponse(ques: str, ans: str):
    global ind
    ind = (ind + 1) % length
    prompt = (f'I want you to help me evaluate the answers of my students and provide appropriate marks'
              f'The Question is\n'
              f'{ques}'
              f'\n'
              f'And the answer written is\n'
              f'{ans}'
              f'\n'
              f'The total marks are written above in brackets with the question\n'
              f'analyze it with respect to organizational behaviour if possible.\n'
              f'How much should he get. Simply Give me a number. After that explain the points where he could have '
              f'improved')
    return getOutput(prompt, all_keys, ind)


def main():
    global id
    st.title('Evaluating answers')
    id = st.text_input(label='Enter id of the test you conducted')
    if id:
        pass


def retrive_csv(filename):
    cloudpath = f'responses/{filename}'
    storage.child(cloudpath).download(filename, filename)


def retrive_json():
    filename = 'credentials.json'
    cloudpath = f'userdata/{filename}'
    storage.child(cloudpath).download(filename, filename)


if __name__ == '__main__':
    main()
    print(all_keys)

    print(id)
    if id:
        retrive_csv(f'ans_{id}.csv')
        file = open(f'ans_{id}.csv', encoding='utf-8')
        st.success('File received successfully')
        csvreader = csv.reader(file, delimiter='`')
        header = []
        header = next(csvreader)
        print(header)

        answers = {}
        for row in csvreader:
            answers[row[-3]] = []
            l = len(row)
            for i in range(-4, -l, -1):
                answers[row[-3]].append(row[i])

            answers[row[-3]].reverse()

        evaluated_answers = {}
        print(answers)
        print('before pop header = ', header)
        header.pop(0)
        header.pop()
        header.pop()
        header.pop()
        print(header)
        user_cred_dict = json.loads(open('credentials.json').read().strip())

        def get_list(key: str):
            evaluated_answers[key] = []
            for i in range(len(header)):
                evaluated_answers[key].append(
                    getResponse(header[i], answers[key][i]))
            print(evaluated_answers[key])

        all_threads = []
        for k in answers.keys():
            t = threading.Thread(target=get_list, args=[k])
            all_threads.append(t)
            t.start()

        for thread in all_threads:
            thread.join()
        for key in evaluated_answers:
            file_name = key + ".md"
            details = f'REG NO: {key}\n\n'
            print('header ====', header)
            print('ans = ', answers[key])
            for i in range(len(header)):
                details += "**" + header[i].strip() + "**\n\n"
                details += answers[key][i] + '\n\n'
                details += evaluated_answers[key][i] + '\n\n'

            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(details)
            os.system(f'pandoc {file_name} -o {key}.pdf')
            if key in user_cred_dict:
                print('key is ', key, 'data is ', user_cred_dict)
                sendMessage(user_cred_dict[key], f'{key}.pdf')
                st.success(f'Email sent to {user_cred_dict[key]}')
            else:
                st.warning(
                    f'Please create account first for registration number {key}')

            st.success('Files Created Successfully results are out')

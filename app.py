import streamlit as st
from st_pages import hide_pages
from streamlit_option_menu import option_menu
import Teacher as Teacher
import Student as Student

st.set_page_config(
    page_title="Test App",
)

hide_pages(["archana", "tashu", "app", "evaluate"])


class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # app = st.sidebar(
        with st.sidebar:
            app = option_menu(
                menu_title='Choose Role',
                options=['Student', 'Teacher'],
                icons=list(reversed(['person-lock', 'person-circle'])),
                menu_icon='clipboard-check',
                default_index=0,
                styles={
                    "container": {"padding": "5!important"},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {"color": "white", "font-size": "18px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "grey", "font-family": "Times New Roman"}}

            )

        if app == "Student":
            Student.app()
        if app == "Teacher":
            Teacher.app()

    run()

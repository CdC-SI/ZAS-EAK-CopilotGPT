import streamlit as st
import requests
from typing import List
from streamlit_searchbox import st_searchbox

if 'last_question' not in st.session_state:
        st.session_state['last_question'] = "x"
if 'last_answer' not in st.session_state:
        st.session_state['last_answer'] = "xx"

# Titel der Streamlit-App
st.title('Such-App')

# function with list of labels
def search(searchterm: str) -> List[any]:
    url = f'http://fastapi:8000/search/?question={searchterm}'
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        question = [item['question'] for item in results if 'question' in item]
        st.session_state['last_question'] = question[0]
        answer = [item['answer'] for item in results if 'answer' in item]
        st.session_state['last_answer'] = answer[0]
        return question
    else:
        return []

# pass search function to searchbox
selected_value = st_searchbox(
    search,
    key="expert_searchbox",
    clear_on_submit=True, 

)

if selected_value:
    with st.chat_message("user"):
        st.write(st.session_state['last_question'])

    with st.chat_message("assistant"):
        st.write(st.session_state['last_answer'])

import streamlit as st
import requests
from typing import List, Dict, Any
from streamlit_searchbox import st_searchbox

# Initialisiere eine Session für 'requests'
session = requests.Session()

if 'last_question' not in st.session_state:
    st.session_state['last_question'] = ""
if 'last_answer' not in st.session_state:
    st.session_state['last_answer'] = ""

st.title('Such-App')

def search_question(searchterm: str) -> List[str]:
    """
    Search for questions that match the search term.
    
    :param searchterm: search term
    :return: list of questions
    """
    url = f'http://fastapi:8000/search/?question={searchterm}'
    try:
        response = session.get(url)
        response.raise_for_status()
        results = response.json()
        if results:
            questions = [item['question'] for item in results if 'question' in item]
            return questions[:10]
    except requests.RequestException as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
        return []
    return []

def get_answer(question: str) -> str:
    """
    Get the answer to a question.
    
    :param question: question
    :return: answer
    """
    url = f'http://fastapi:8000/search/?question={question}'
    try:
        response = session.get(url)
        response.raise_for_status()
        results = response.json()
        if results:
            answer = [item['answer'] for item in results if 'answer' in item]
            return answer[0]
    except requests.RequestException as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
        return ""
    return ""

selected_value = st_searchbox(
    search_question,
    key="expert_searchbox",
    clear_on_submit=True,
)

if selected_value:
    st.session_state['last_question'] = selected_value
    with st.chat_message("user"):
        st.write(st.session_state['last_question'])

    st.session_state['last_answer'] = get_answer(selected_value)
    with st.chat_message("assistant"):
        st.write(st.session_state['last_answer'])

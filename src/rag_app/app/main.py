import streamlit as st

st.set_page_config(page_title="RAG Assistant", layout="wide")
st.title("RAG Assistant")

query = st.text_input("Question")
if query:
    st.info("Brancher ici l'appel au pipeline retrieval -> generation.")

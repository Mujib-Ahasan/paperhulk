import streamlit as st

st.set_page_config(
    page_title="PaperLens",
    page_icon="📄",
)

st.title("📄 PaperLens")
st.write("AI-powered research paper summarizer")

uploaded_file = st.file_uploader(
    "Upload a research paper PDF",
    type=["pdf"],
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
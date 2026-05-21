import streamlit as st
from pdf_loader import (
    extract_text_from_pdf,
    extract_images_from_pdf,
    remove_after_conclusion,
    research_paper_score
)
from ollama_client import generate_response
from chunker import chunk_text

st.set_page_config(
    page_title="paperHulk",
    page_icon="📄",
)

st.title("📄 paperHulk")
st.write("AI-powered research paper summarizer")

uploaded_file = st.file_uploader(
    "Upload a research paper PDF",
    type=["pdf"],
)

debug_mode = st.sidebar.checkbox(
    "Debug mode",
    value=False,
)

## this is for test purpose, this should be removed at final.
st.sidebar.subheader("Local LLM Test")

test_prompt = st.sidebar.text_area(
    "Test prompt",
    value="A Large Language Model (LLM) is an advanced AI system trained on massive datasets to process, " \
    "understand, and generate human-like text. Powered by transformer architectures and deep learning, " \
    "these models predict the most likely next words in a sequence to create fluent, context-aware " \
    "responses, and power many modern generative AI applications."
     "Transformer Architecture: The foundational neural network design behind modern LLMs. It enables the model to process large sequences of text simultaneously and track long-range dependencies."
     "Self-Attention Mechanism: A mathematical technique within the transformer that allows the model to weigh the"
      "importance of different words in a sentence relative to one another. This is how an LLM grasps complex context and nuance."
     "Parameters & Training: Parameters are the adjustable elements within the models neural network. During pre-training,"
     "the LLM analyzes petabytes of data—including books, websites, and code—to adjust these parameters and learn language syntax, facts, and reasoning." 
)

if st.sidebar.button("Test Ollama"):
    with st.spinner("Testing Ollama..."):
        response = generate_response(test_prompt)

    st.sidebar.success("Ollama responded!")
    st.sidebar.write(response)

## this is for test purpose, this should be removed at final.

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    try:
        extracted_text = extract_text_from_pdf(uploaded_file)
        cleaned_text = remove_after_conclusion(extracted_text)
        score = research_paper_score(cleaned_text)

        if not cleaned_text:
            st.warning("No readable text found in this PDF.")
        else:
            st.success("Text extracted successfully!")
            if score >=4 and len(cleaned_text.split())>=2500:
               st.success("Research Paper structure detected")
               st.write(f"Extracted characters: {len(cleaned_text)}")
               st.write(f"Estimated words: {len(cleaned_text.split())}")
               st.subheader("Cleaned Extracted Text")
               if debug_mode:
                    st.text_area( "PDF Content",cleaned_text,height=400)
               chunk_size = st.sidebar.number_input("Chunk size", min_value=1000,max_value=8000,value=2500,step=500)
               overlap = st.sidebar.number_input("Chunk overlap", min_value=0, max_value=1000, value=200,step=100)

               chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)

               st.write(f"Generated chunks: {len(chunks)}")
               if debug_mode:
                    with st.expander("View Chunks"):
                        for index, chunk in enumerate(chunks, start=1):
                            st.markdown(f"### Chunk {index}")
                            st.text_area(f"Chunk {index}", chunk, height=200)
            else:
               st.warning("This PDF may not be a research paper, can not process it")
  
        uploaded_file.seek(0)
        image_paths = extract_images_from_pdf(uploaded_file)

        st.subheader("Extracted Images")

        if not image_paths:
            st.info("No images detected.")
        else:
            for image in image_paths:
                st.write(f"Page {image['page']}")
                st.write(image["caption"])
                st.image(image["path"], use_container_width=True)

    except Exception as err:
        st.error(f"Failed to process PDF: {err}")
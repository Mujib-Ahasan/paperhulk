import streamlit as st
from pdf_loader import (
    extract_text_from_pdf,
    extract_images_from_pdf,
    remove_after_conclusion,
    research_paper_score
)
from chunker import chunk_text
from config import CHUNK_SIZE, CHUNK_OVERLAP
from summarizer import summarize_paper

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

               chunks = chunk_text(cleaned_text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
               if st.button("Generate Summary"):
                    with st.spinner("Generating summary..."):
                        summary = summarize_paper(chunks)

                    st.subheader("Final Summary")
                    st.write(summary)
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
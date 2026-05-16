import streamlit as st
from pdf_loader import (
    extract_text_from_pdf,
    extract_images_from_pdf,
    remove_after_conclusion,
    extract_figure_captions
)

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

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    try:
        extracted_text = extract_text_from_pdf(uploaded_file)
        cleaned_text = remove_after_conclusion(extracted_text)


        if not cleaned_text:
            st.warning("No readable text found in this PDF.")
        else:
            st.success("Text extracted successfully!")
            st.write(f"Extracted characters: {len(cleaned_text)}")
            st.write(f"Estimated words: {len(cleaned_text.split())}")

            st.subheader("Cleaned Extracted Text")
            st.text_area(
                "PDF Content",
                cleaned_text,
                height=400,
            )

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
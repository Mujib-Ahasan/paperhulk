import fitz 
import os
import re


import fitz


def extract_text_from_pdf(uploaded_file) -> str:
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    pages_text = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page_num, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")
            page_lines = []

            for block in blocks:
                text = block[4].strip()

                if not text:
                    continue

                # Skip likely table/caption-heavy blocks
                if is_noisy_table_block(text):
                    continue

                page_lines.append(text)

            pages_text.append(
                f"\n\n--- Page {page_num} ---\n" + "\n".join(page_lines)
            )

    return "\n".join(pages_text).strip()


def is_noisy_table_block(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return True

    # Skip table captions and table-heavy blocks
    if lines[0].lower().startswith("table "):
        return True

    numeric_lines = 0
    short_lines = 0

    for line in lines:
        words = line.split()

        if len(words) <= 3:
            short_lines += 1

        if any(char.isdigit() for char in line):
            numeric_lines += 1

    # Tables often have many short/numeric rows
    if len(lines) > 5 and short_lines / len(lines) > 0.6:
        return True

    if len(lines) > 5 and numeric_lines / len(lines) > 0.5:
        return True

    return False


def extract_images_from_pdf(uploaded_file, output_dir="images"):
    pdf_bytes = uploaded_file.read()

    os.makedirs(output_dir, exist_ok=True)

    image_paths = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
      for page_index in range(len(doc)):
        page = doc[page_index]

        image_list = page.get_images(full=True)

        page_text = page.get_text("text")
        captions = extract_figure_captions(page_text)

        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]

            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_name = (
                f"page_{page_index+1}_img_{image_index}.{image_ext}"
            )

            image_path = os.path.join(output_dir, image_name)

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            caption = (
                captions[image_index - 1]
                if image_index - 1 < len(captions)
                else "Unknown Figure"
            )

            image_paths.append({
                "page": page_index + 1,
                "path": image_path,
                "caption": caption,
            })

    return image_paths



def remove_after_conclusion(text: str) -> str:
    stop_patterns = [
        r"\n\s*references\s*\n",
        r"\n\s*bibliography\s*\n",
        r"\n\s*appendix\s*\n",
        r"\n\s*acknowledg(e)?ments\s*\n",
        r"\n\s*supplementary material\s*\n",
    ]

    lower_text = text.lower()

    cut_positions = []

    for pattern in stop_patterns:
        match = re.search(pattern, lower_text, re.IGNORECASE)
        if match:
            cut_positions.append(match.start())

    if not cut_positions:
        return text

    return text[:min(cut_positions)].strip()

def extract_figure_captions(text: str) -> list[str]:
    captions = []

    patterns = [
        r"(Figure\s+\d+[:.].*)",
        r"(Fig\.\s*\d+[:.].*)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            captions.append(match.strip())

    return captions

def research_paper_score(text: str) -> int:
    text = text.lower()

    keywords = [
        "abstract",
        "introduction",
        "related work",
        "methodology",
        "results",
        "discussion",
        "conclusion",
        "references",
    ]

    score = 0

    for keyword in keywords:
        if keyword in text:
            score += 1

    return score
from config import CHUNK_SUMMARY_WORD_LIMIT

def final_summary_prompt(combined_summary: str, mode: str = "technical") -> str:
    if mode == "simple":
        return f"""
You are explaining a research paper to a 10-year-old.

Create one final simple summary.

Include:
- Problem statement
- Proposed approach
- Key contributions
- Methodology
- Results
- Limitations if mentioned
- Conclusion

Keep it clear and beginner-friendly.

Below are summaries of different parts of a research paper.

Section summaries:
{combined_summary}
"""

    return f"""
You are an expert research paper summarizer.

Create one final structured technical summary.

Include:
- Problem statement
- Proposed approach
- Key contributions
- Methodology
- Results
- Limitations if mentioned
- Conclusion

Keep it concise, readable, and technically accurate.

Below are summaries of different parts of a research paper.

Section summaries:
{combined_summary}
"""

def technical_summary_prompt(text: str) -> str:
    return f"""
You are an expert research paper summarizer.

Summarize the following research paper section.

Requirements:
- Maximum {CHUNK_SUMMARY_WORD_LIMIT} words
- Keep the summary concise and technical
- Focus on the main problem, method, contribution, and findings
- Mention limitations if present

Text:
{text}
"""

def simple_summary_prompt(text: str) -> str:
    return f"""
Explain the following research paper section like I am 10 years old.

Requirements:
- Maximum {CHUNK_SUMMARY_WORD_LIMIT} words
- Use simple words
- Avoid technical jargon
- Keep the explanation easy to understand

Text:
{text}
"""
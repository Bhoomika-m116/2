from docx import Document
from docx.shared import Pt
from .risk_extractor import underline_risk_sentences
import os

def generate_docx(summary_html, raw_text, output_path, keywords=None):
    """Create a .docx file with the same underlined risk sentences.
    ``summary_html`` contains <u> tags which we translate to underline formatting.
    """
    doc = Document()
    doc.add_heading('Executive Summary', level=1)
    # Convert simple HTML <u> to underline runs
    import re
    # split by <u> tags
    parts = re.split(r'(<u>|</u>)', summary_html)
    paragraph = doc.add_paragraph()
    underline = False
    for part in parts:
        if part == '<u>':
            underline = True
            continue
        if part == '</u>':
            underline = False
            continue
        run = paragraph.add_run(part)
        if underline:
            run.underline = True
        run.font.size = Pt(11)
    doc.add_page_break()
    # Risk Factors section
    doc.add_heading('Risk Factors', level=2)
    from .risk_extractor import extract_risk_clauses
    risk_sentences = extract_risk_clauses(raw_text, keywords)
    for rs in risk_sentences:
        p = doc.add_paragraph()
        p.add_run(rs).underline = True
    doc.save(output_path)
    return {'docx_path': output_path}

import os
import json
from datetime import datetime
from .nlp_preprocessor import detect_language, preprocess_text
from .risk_extractor import underline_risk_sentences
from .report_generator import generate_pdf
from .word_exporter import generate_docx

def process_document(file_path, user_id):
    """Full pipeline: OCR (if image), language detection, summarise, risk extraction, PDF/Word export.
    Returns dict with paths and timestamp.
    """
    # For simplicity, assume input is a plain text file or PDF converted to text elsewhere.
    # Here we just read the file.
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()

    # Save raw text for auditability
    raw_dir = os.path.join(os.path.dirname(file_path), 'raw_texts')
    os.makedirs(raw_dir, exist_ok=True)
    raw_filename = f"raw_{os.path.basename(file_path)}_{int(datetime.utcnow().timestamp())}.txt"
    raw_path = os.path.join(raw_dir, raw_filename)
    with open(raw_path, 'w', encoding='utf-8') as f:
        f.write(raw_text)

    # Language detection
    lang = detect_language(raw_text)
    # Preprocess (tokenize etc.) – we just split into sentences for a naive summary
    sentences = raw_text.split('.')
    # Very naive summarisation: take first 5 sentences
    summary_sentences = [s.strip() for s in sentences if s.strip()][:5]
    summary_text = '. '.join(summary_sentences) + ('.' if summary_sentences else '')

    # Underline risk sentences in the summary for PDF/Word
    keywords = None  # risk_extractor will load defaults
    underlined_summary = underline_risk_sentences(summary_text, keywords)

    # Generate PDF
    pdf_output = os.path.join(os.path.dirname(file_path), f"summary_{int(datetime.utcnow().timestamp())}.pdf")
    pdf_info = generate_pdf(underlined_summary, raw_text, pdf_output, keywords)

    # Generate Word
    docx_output = os.path.join(os.path.dirname(file_path), f"summary_{int(datetime.utcnow().timestamp())}.docx")
    generate_docx(underlined_summary, raw_text, docx_output, keywords)

    return {
        'pdf_path': pdf_info['pdf_path'],
        'docx_path': docx_output,
        'raw_text_path': raw_path,
        'timestamp': pdf_info['timestamp']
    }

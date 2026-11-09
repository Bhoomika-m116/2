from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
import os
import json
from datetime import datetime
from .risk_extractor import underline_risk_sentences, extract_risk_clauses


def generate_pdf(summary_text, raw_text, output_path, risk_keywords=None):
    """Create a PDF report with underlined risk sentences and a simple heat‑map bar.
    Returns a dict with paths and timestamp.
    """
    # Underline risk sentences in the summary (HTML -> simple ReportLab markup)
    underlined = underline_risk_sentences(summary_text, risk_keywords)

    doc = SimpleDocTemplate(output_path, pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph('Executive Summary', styles['Title']))
    story.append(Spacer(1, 12))
    # Summary paragraph (ReportLab supports a subset of HTML tags like <u>)
    story.append(Paragraph(underlined, styles['Normal']))
    story.append(Spacer(1, 12))

    # Risk Factors Section
    story.append(Paragraph('Risk Factors', styles['Heading2']))
    risk_sentences = extract_risk_clauses(raw_text, risk_keywords)
    for rs in risk_sentences:
        story.append(Paragraph(f'<u>{rs}</u>', styles['Normal']))
        story.append(Spacer(1, 6))
    story.append(Spacer(1, 12))

    # Simple heat‑map graphic (severity based on count of risk sentences)
    severity = min(len(risk_sentences), 10)  # cap at 10 for colour scale
    bar_width = 400
    bar_height = 20
    drawing = Drawing(bar_width, bar_height)
    # background
    drawing.add(Rect(0, 0, bar_width, bar_height, fillColor=colors.lightgrey))
    # filled portion proportional to severity
    filled_width = (severity / 10) * bar_width
    drawing.add(Rect(0, 0, filled_width, bar_height, fillColor=colors.red))
    story.append(Paragraph('Risk Score Heatmap', styles['Heading3']))
    story.append(drawing)

    doc.build(story)
    return {
        'pdf_path': output_path,
        'timestamp': datetime.utcnow(),
        'risk_sentences': risk_sentences,
    }

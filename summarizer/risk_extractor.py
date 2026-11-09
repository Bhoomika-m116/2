import re
from .nlp_preprocessor import load_keyword_list


def underline_risk_sentences(html_text, keywords=None):
    """Wrap risk‑related sentences in <u>…</u> tags.
    The input ``html_text`` is a plain string (Paragraph text) – we split on punctuation.
    Returns the modified string with <u> tags.
    """
    if keywords is None:
        keywords = load_keyword_list()
    # Build regex pattern for any keyword (case‑insensitive)
    pattern = re.compile(r'(' + '|'.join(map(re.escape, keywords)) + r')', re.IGNORECASE)
    # Split into sentences (very simple split on '.' '?', '!')
    sentences = re.split(r'(?<=[.!?])\s+', html_text)
    processed = []
    for s in sentences:
        if pattern.search(s):
            processed.append(f'<u>{s.strip()}</u>')
        else:
            processed.append(s.strip())
    return ' '.join(processed)


def extract_risk_clauses(text, keywords=None):
    """Return a list of raw risk sentences (without HTML)."""
    if keywords is None:
        keywords = load_keyword_list()
    pattern = re.compile(r'(' + '|'.join(map(re.escape, keywords)) + r')', re.IGNORECASE)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if pattern.search(s)]

import os
import pytesseract
from PIL import Image
import cv2
from langdetect import detect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import json

# Ensure NLTK data is available (download if missing)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def ocr_image_to_text(image_path):
    """Run OCR on an image file and return extracted text."""
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def detect_language(text):
    """Detect language code (e.g., 'en', 'fr')."""
    try:
        return detect(text)
    except Exception:
        return 'en'

def preprocess_text(raw_text, lang='en'):
    """Basic preprocessing: tokenization, lowercasing, stop‑word removal.
    Returns a list of sentences ready for summarisation.
    """
    stop_words = set(stopwords.words(lang)) if lang in stopwords.fileids() else set()
    sentences = sent_tokenize(raw_text)
    cleaned = []
    for s in sentences:
        words = [w.lower() for w in word_tokenize(s) if w.isalnum() and w.lower() not in stop_words]
        cleaned.append(' '.join(words))
    return cleaned

def load_keyword_list():
    """Load risk keywords from the DB via Keyword model – placeholder for now.
    This function will be overridden in the pipeline where DB session is available.
    """
    # default fallback list
    return ["risk", "liability", "exposure", "penalty", "fine", "danger", "hazard", "threat"]

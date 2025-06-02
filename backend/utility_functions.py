"""
Thomas De Sa - 2025-06-02

Utility functions for backend
"""
import spacy
from ethics_categories import ETHICS_CATEGORIES

nlp = spacy.load("en_core_web_sm")


def categorize(headline):
    """Tokenizes headline then categorizes article based on keyword matching.
    See ethics_categories.py

    Args:
        headline (str): Article headline

    Returns:
        list: array of categories article matched (see ETHICS_CATEGORIES dict)
    """
    doc = nlp(headline.lower())
    tokens = [token.text for token in doc]
    
    categories = []
    for category, keywords in ETHICS_CATEGORIES.items():
        for keyword in keywords:
            if any(keyword in token for token in tokens):
                categories.append(category)
                break
            
    return categories or ["uncategorized"]

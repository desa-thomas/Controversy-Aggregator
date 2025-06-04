"""
Thomas De Sa - 2025-06-04
"""

import spacy
from ethics_categories import ETHICS_CATEGORIES
nlp = spacy.load("en_core_web_sm")

class Article:

    def __init__(self, company: str, headline: str, url: str, source: str, categories: list[str], date_published:str):
        """Initalize Article object

        Args:
            company (str): Name of company article is about
            headline (str): Headline of article
            url (str): URL of article
            source (str): Name of new outlet which published the article
            categories (list[str]): List of ethical categories that article is categorized into
            date_published (_type_): Date article was published
        """ 
        self.company = company
        self.headline = headline
        self.url = url
        self.source = source
        self.categories = categories
        self.date_published = date_published
        
    def get_articles(company:str):
        pass
        
    def categorize(headline:str):
        """Static function. 
        Tokenizes headline then categorizes article based on keyword matching.
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

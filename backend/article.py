"""
Thomas De Sa - 2025-06-04
"""

import requests
from ethics_categories import ETHICS_CATEGORIES
from config import API_KEY

class Article:

    GNEWS_ENDPOINT = "https://gnews.io/api/v4/search"
    
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
        
    def get_articles(company:str, category:str, session:requests.Session = None):
        category = category.lower()
        if category not in ETHICS_CATEGORIES.keys() and category != "all":
            print("Invalid category")
        
        
        query = f'"{company}" AND ({category} OR {" OR ".join(ETHICS_CATEGORIES[category])})'
        print(query)
        print(len(query))
        
        # if session: pass
        
        # else:
        #     requests.get(Article.GNEWS_ENDPOINT + f'?q=apikey={API_KEY}')

        return 
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
        """Get articles form GNEWS API relating to a specific company and ethical category

        Args:
            company (str): Name of company
            category (str): Ethical category (relating to keys of ETHICAL_CATEGORIES dict. ethics_categories.py)
            session (requests.Session, optional): Requests session. Defaults to None.
        
        return:
            json ()
        """
        category = category.lower()
        json = None
        gen = False
        
        if category not in ETHICS_CATEGORIES.keys() and category != "all":
            print("Invalid category")
        
        else: 
            #generate GNEWS API query. Doumentation here: https://gnews.io/docs/v4?python#search-endpoint
            query = f'"{company}" AND ({category} OR {" OR ".join(ETHICS_CATEGORIES[category])})'
            
            if not session:
                gen = True
                session = requests.Session()
                
            res = session.get(Article.GNEWS_ENDPOINT + f'?q={query}&lang=en&apikey={API_KEY}')
            
            print(f"code: {res.status_code}")
            
            if res.json:
                json = res.json()
            
            if gen:
                session.close()
            
        return json, res.status_code
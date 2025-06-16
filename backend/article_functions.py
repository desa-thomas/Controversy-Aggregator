"""
Thomas De Sa - 2025-06-04

GNEW DOCS: gnews.io/docs/v4 
"""

import requests
from datetime import datetime
from ethics_categories import ETHICS_CATEGORIES
from config import API_KEY
from database_functions import company_exists
from models import Article

GNEWS_ENDPOINT = "https://gnews.io/api/v4/search"

    
def get_articles(company:str, category:str, session:requests.Session = None):
    """Static function. Get articles form GNEWS API relating to a specific company and ethical category

    Args:
        company (str): Name of company
        category (str): Ethical category (relating to keys of ETHICAL_CATEGORIES dict. ethics_categories.py)
        session (requests.Session, optional): Requests session. Defaults to None.
    
    return:
        json ()
    """
    category = category.lower()
    
    articles = []
    
    #generated session
    gen = False
    
    if category not in ETHICS_CATEGORIES.keys() and category != "all":
        print("Invalid category")
    
    elif not company_exists(company):
        print(f"{company} not in database")
        
    else: 
        #generate GNEWS API query. Doumentation here: https://gnews.io/docs/v4?python#search-endpoint
        query = f'"{company}" AND ({" OR ".join(ETHICS_CATEGORIES[category])})'
        
        if not session:
            gen = True
            session = requests.Session()
            
        res = session.get(GNEWS_ENDPOINT + f'?q={query}&lang=en&apikey={API_KEY}')
        
        print(f"code: {res.status_code}")
        
        if res.ok and res.json:
            json = res.json()
            articles_json = json["articles"]
            
            for article in articles_json:
                categories = get_categories(article['title'], article['description'])
                
                article_obj = Article(company, 
                                    article["title"], 
                                    article["url"], 
                                    article["source"]["name"], 
                                    categories,
                                    datetime.fromisoformat(article["publishedAt"].replace("Z", "")),
                                    article['description'])
                articles.append(article_obj)
        
        if gen:
            session.close()

    return articles

def get_categories(headline:str, description:str):
    """Get all categories for an article

    Args:
        headline (str): headline
    """
    categories = []
    for category in ETHICS_CATEGORIES.keys():
        
        #if any keyword appears in description or headline
        if any(kw for kw in ETHICS_CATEGORIES[category] if (kw.lower() in description.lower() or kw.lower() in headline.lower())):
            categories.append(category)
    
    return categories


"""
Thomas De Sa - 2025-06-04

GNEW DOCS: gnews.io/docs/v4 
"""

import requests
from datetime import datetime
from ethics_categories import ETHICS_CATEGORIES
from config import API_KEY
from database_functions import company_exists, get_found
from models import Article

GNEWS_ENDPOINT = "https://gnews.io/api/v4/search"

    
def get_articles(company:str, category:str, to:datetime = None, session:requests.Session = None):
    """Static function. Get articles form GNEWS API relating to a specific company and ethical category

    Args:
        company (str): Name of company
        category (str): Ethical category (relating to keys of ETHICAL_CATEGORIES dict. ethics_categories.py)
        session (requests.Session, optional): Requests session. Defaults to None.
    
    return:
        tuple (articles, found): returns array of article objects retrieved, and total amount of articles found on the query
    """
    category = category.lower()
    
    articles = []
    articles_found = 0
    
    #generated session
    gen = False
    
    if category not in ETHICS_CATEGORIES.keys():
        print("Invalid category")
    
    elif not company_exists(company):
        print(f"{company} not in database")
        
    else: 
        #generate GNEWS API query. Doumentation here: https://gnews.io/docs/v4?python#search-endpoint
        query = f'"{company}" AND ({" OR ".join(ETHICS_CATEGORIES[category])})'
        params = {
            'q': query,
            'lang': "en",
            "apikey": API_KEY
        }
        if to:
            params["to"] = to_iso(to)
            
        if not session:
            gen = True
            session = requests.Session()
            
        res = session.get(GNEWS_ENDPOINT, params= params)
        
        print(f"code: {res.status_code}")
        
        if res.ok and res.json:
            json = res.json()
            articles_json = json["articles"]
            articles_found = json["totalArticles"]
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

    return articles, articles_found

def get_categories(headline:str, description:str):
    """Get all categories for an article

    Args:
        headline (str): headline
    """
    categories = []
    for category in ETHICS_CATEGORIES.keys():
        
        #if any keyword appears in description or headline
        if any(kw.strip('"') for kw in ETHICS_CATEGORIES[category] if (kw.lower().strip('"') in description.lower() or kw.lower().strip('"') in headline.lower())):
            categories.append(category)
    
    return categories

def to_iso(date:datetime):
    """Convert datetime obj to iso format for GNEWS"""
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')


#TODO Article retrieval based on paging, check database for articles, use GNEWS when necessary to update db
def fetch_articles(company:str, page: int, category:str = None):
    """Wrapper for get_articles, and retrieve_articles.
    Gets all articles for a company and category.
    
    Checks to see if articles are stored in database, if not
    gets them from GNEWS API. 
    
    pages are in increments of 10 articles. 

    Args:
        company (str): name of company
        page (int): page number of articles to retrieve
    """
    
    #page in range
    if page <= get_num_of_pages(company, category):
        pass

    else:
        print("Page out of range")
    
    pass

def get_num_of_pages(company:str, category:str=None):
    
    found = get_found(company, category)
    return found//10


"""
Thomas De Sa - 2025-06-04

GNEW DOCS: gnews.io/docs/v4 
"""

import requests
from datetime import datetime, timedelta
import time
from mysql.connector import Error


#Created modules
from ethics_categories import ETHICS_CATEGORIES
from config import API_KEY
from database_functions import *
from models import Article, pageNotInDatabaseError, APILimitReached

GNEWS_ENDPOINT = "https://gnews.io/api/v4/search"

    
def get_articles(company:str, category:str, to:datetime = None, session:requests.Session = None):
    """Static function. Get articles form GNEWS API relating to a specific company and ethical category

    Args:
        company (str): Name of company
        category (str): Ethical category (relating to keys of ETHICAL_CATEGORIES dict. ethics_categories.py)
        session (requests.Session, optional): Requests session. Defaults to None.
    
    Raises:
        APILimitReached: API Limit on GNEWS Reached
        
    ## Return:
        **articles** : returns array of article objects retrieved, 
        **found**: total amount of articles found on the query
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
        
        print(f"get_articles({company}) - code: {res.status_code}")
        
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
        elif res.status_code == 403:
            raise APILimitReached("API Limit Reached")
        
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


def fetch_articles(company:str, page: int, category:str = None):
    """High level function which combines `get_and_store_articles()` and `get_page()` to retrieve a page of articles.
    Checks to see if page is stored in database, if not, retrieve from GNEWS.
    
    Checks to see if articles are stored in database, if not
    gets them from GNEWS API. 
    
    pages are in increments of 10 articles. 

    Args:
        company (str): name of company
        page (int): page number of articles to retrieve
    
    Raises:
        Exception: Page out of range or page number is not one greater than currently stored in db
        
    returns:
        List of articles in page
    """
    num_articles = get_found(company, category)
    total_pages = calculate_pages(num_articles)
    articles = []
    
    #If first page, check if needs cached articles need updating
    if page == 1:
        timestamp = get_cache_timestamp(company, category)
        twodays = datetime.now()- timedelta(days=2)
        if timestamp <= twodays:
            get_and_store_articles(company, category, retrieve_old=False) #i.e., update
        else:
            print("Cached articles up to date")
        
    if page <= total_pages and page > 0:
        
        #I will limit the client side so that you can only request a page at a time,
        #so requesting once should suffice
        while not articles:
            try:
                articles = get_page(company, page, category)
                
            except pageNotInDatabaseError as e:
                if e.db_pages + 1 != page:
                    raise Exception(f"Page index too large, must be 1 greater than currently available. Currently available pages: {e.db_pages}/{total_pages}")
                    
                get_and_store_articles(company, category, retrieve_old=True)    
        
    else:
        raise Exception(f"Page {page} out of range for Company: {company} - Category: {category}. Total pages: {total_pages}")
    
    return articles

def get_and_store_articles(company:str, category:str = None, retrieve_old:bool = False):
    """Combines `get_articles()` and `insert_articles()` and `insert_found()` into one wrapper function
    maintains one persistent db connection and retrieves articles from GNEWS and inserts all relevant article data into 
    database.
    NOTE: retrieve_old toggles whether to get older articles from GNEWS (earlier than oldest in db) or check new articles

    Args:
        company (str): name of company  
        category (str, optional): category of articles to retrieve, if None get all. Defaults to None.
        retrieve_old (bool, optional): whether to retrieve old articles, other wise retrieves new ones. Defaults to None.
    
    Raises:
        APILimitReached: Limit on GNEWS API Reached
    
    returns:
        None
    """
    #Only add 'to' parameter if retrieve_old is toggled
    to = None
    arr = ETHICS_CATEGORIES
    if category: arr = [category]
    
    try:
        with db_connection() as connection:
            print(connection)
 
            for category in arr:
                if retrieve_old: 
                    to = get_oldest_date(company, connection, category)
                
                articles, found =  get_articles(company, category, to=to)
                
                insert_articles(articles, connection)
                insert_found(company, category, found, connection)
                time.sleep(1)
                    
            connection.commit()
            
    except Error as e:
        print(e)
        
    return 

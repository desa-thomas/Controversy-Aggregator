""" 
Thomas De Sa 2025-06-16

Functions for performing CRUD operations on database.
... API for database
"""

from models import Article
from mysql.connector import connect, Error
from config import db_host, db_pass, db_user, db_name
from ethics_categories import ETHICS_CATEGORIES

#Create 
def insert_article(article: Article):
    """Insert article into article table and corresponding categories to category table.

    Args:
        article (Article): article
    """
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            
            #Ignore articles with identical urls
            article_query = """
            INSERT IGNORE INTO articles (company_name, title, description, url, source, published_date, retrieved)
            VALUES (%s, %s, %s, %s, %s,%s, NOW())"""
            
            category_query = """
            INSERT IGNORE INTO categories (id, category)
            VALUES (%s, %s)"""
            
            with connection.cursor() as cursor:
                cursor.execute(article_query, (article.company, article.headline, article.description, article.url, article.source, article.date_published))

                id = cursor.lastrowid
                for category in article.categories: 
                    cursor.execute(category_query, (id, category))
                
                print(f"{cursor.rowcount} rows affected")
            connection.commit()
            
            
    except Error as e: 
        print(e)

def insert_found(company: str, category:str, found:int, update = False): 
    """Insert the # of found articles (from GNEWS) to the db

    Args:
        company (str): Name of company      
        category (str): Category of search
        found (int): num of found articles
        update (bool): whether to update value if found. ONLY UPDATE IF ARTICLE SEARCH HAD NO DATE RESTRICTION
    """
    if update:  
        query = """
        INSERT INTO found (company, category, found)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            found = VALUES(found)"""
    else:
        query = """
        INSERT IGNORE INTO found (company, cateogry, foudn)
        VALUES (%s, %s, %s)"""     
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (company, category, found))
                    
            connection.commit()
            print(f"Inserted {company} - {category}: {found}")
            
    except Error as e:
        print(e)    


#Read
def retrieve_articles(company:str, limit:int = None):
    """retrieve articles on company from database

    Args:
        company (str): name of company
        limit(int): limit on number of articles retrieved 
    """
    
    articles = []
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            query = """
            SELECT * FROM articles WHERE company_name = %s ORDER BY published_date DESC"""
            
            if limit and isinstance(limit, int): 
                query += f" LIMIT {limit}"
                
            categories_query = """SELECT category FROM categories WHERE id = %s"""

            with connection.cursor() as cursor:
                cursor.execute(query, (company,))
                results = cursor.fetchall()

                
                if results:
                    for row in results:
                        #Get categories from categories table
                        cursor.execute(categories_query, (row[0],))
                        categories = []
                        cat_results = cursor.fetchall()
                        
                        for cat_row in cat_results:
                            categories.append(cat_row[0])
                        
                        #Refer to util/database_setup.py create_tables() for table schemas
                        article = Article(row[1], row[2], row[4], row[5], categories, row[6], row[3], retrieved=row[7])

                        articles.append(article)
                else:
                    print(f"no articles on {company} found")
    except Error as e:
        print(e)
    
    return articles

def get_oldest_date(company: str, category:str = None):
    """Get the date of the oldest article stored in the database (of a particular company)

    Args:
        company (str): company
        category (str, optional): category to search for. Defaults to None.

    Returns:
        datetime: date of oldest article
    """    
    date = None
    if category:
        if category not in ETHICS_CATEGORIES.keys():
            print(f"Invalid category: {category}")
            return
        query = """SELECT published_date FROM articles
        JOIN categories ON articles.id = categories.id
        WHERE categories.category = %s
        ORDER BY articles.published_date ASC
        LIMIT 1"""
    
    else:
        query = """
        SELECT published_date FROM articles 
        ORDER BY published_date ASC
        LIMIT 1"""
        
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:

            with connection.cursor() as cursor:
                if category:
                    cursor.execute(query, (category,))
                else:
                    cursor.execute(query)
                    
                results = cursor.fetchall()
                date = results[0][0]
    except Error as e:
        print(e)
    
    return date

#TODO
def retrieve_industries(company:str):
    """retrive industries of a company

    Args:
        company (str): _description_
    """
    pass

def company_exists (company:str):
    """Check if company exists in database

    Args:
        company (str): _description_
    """
    exists = False
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM companies WHERE name = %s", (company, ))
                exists = len(cursor.fetchall()) == 1
    except Error as e:
        print(e)

    return exists

#TODO
def category_count(company:str, category:str):
    """Return count of articles involving a company and a specific category

    Args:
        company (str): _description_
        category (str): _description_
    """
    pass
#Update

#Delete
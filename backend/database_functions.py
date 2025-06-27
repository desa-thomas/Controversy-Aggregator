""" 
Thomas De Sa 2025-06-16

Functions for performing CRUD operations on database.
... API for database
"""

from models import Article, pageNotInDatabaseError
from mysql.connector import connect, Error
from config import db_host, db_pass, db_user, db_name
from ethics_categories import ETHICS_CATEGORIES


def db_connection():
    return connect(host=db_host, user=db_user, password=db_pass, database=db_name)

# Create


def insert_article(article: Article):
    """Insert article into article table and corresponding categories to category table.

    Args:
        article (Article): article
    """
    with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
        print(connection)

        # Ignore articles with identical urls
        article_query = """
        INSERT INTO articles (title, description, url, source, published_date, retrieved)
        VALUES (%s, %s, %s, %s,%s, NOW())
        ON DUPLICATE KEY UPDATE
            retrieved = NOW()"""

        category_query = """
        INSERT IGNORE INTO categories (id, category)
        VALUES (%s, %s)"""

        articles_companies_query = """
        INSERT IGNORE INTO articles_companies (id, company)
        VALUES (%s, %s)"""

        with connection.cursor() as cursor:
            cursor.execute(article_query, (article.headline, article.description,
                            article.url, article.source, article.date_published))

            id = cursor.lastrowid
            for category in article.categories:
                cursor.execute(category_query, (id, category))

            cursor.execute(articles_companies_query, (id, article.company))
            print(f"{cursor.rowcount} rows affected")
        connection.commit()



def insert_articles(articles: list[Article], connection):

    # Ignore articles with identical urls
    article_query = """
    INSERT INTO articles (title, description, url, source, published_date, retrieved)
    VALUES ( %s, %s, %s, %s,%s, NOW())
    ON DUPLICATE KEY UPDATE
        retrieved = NOW()"""

    category_query = """
    INSERT IGNORE INTO categories (id, category)
    VALUES (%s, %s)"""

    articles_companies_query = """
            INSERT IGNORE INTO articles_companies (id, company)
            VALUES (%s, %s)"""

    with connection.cursor() as cursor:
        for article in articles:
            cursor.execute(article_query, (article.headline, article.description, article.url, article.source, article.date_published))

            id = cursor.lastrowid
            for category in article.categories:
                cursor.execute(category_query, (id, category))

            cursor.execute(articles_companies_query, (id, article.company))
            
            print(f"{cursor.rowcount} rows affected")
    connection.commit()


def insert_found(company: str, category: str, found: int, connection, update=True):
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
            found = GREATEST(found, VALUES(found))"""
    else:
        query = """
        INSERT IGNORE INTO found (company, category, found)
        VALUES (%s, %s, %s)"""

    with connection.cursor() as cursor:
        cursor.execute(query, (company, category, found))

    connection.commit()

    print(f"Inserted {company} - {category}: {found}")


# Read
def retrieve_articles(company: str, category: str = None, limit: int = None):
    """retrieve articles on company from database

    Args:
        company (str): name of company
        limit(int): limit on number of articles retrieved 
    """

    articles = []
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            if category:
                query = """
                SELECT * FROM articles a
                JOIN categories ON categories.id = a.id
                JOIN articles_companies ac ON ac.id = a.id
                WHERE company = %s AND category = %s
                ORDER BY published_date DESC
                """
                params = (company, category)
            else:
                query = """SELECT * 
                FROM articles 
                JOIN articles_companies ac ON articles.id = ac.id
                WHERE company = %s ORDER BY published_date DESC"""
                params = (company, )

            if limit and isinstance(limit, int):
                query += f" LIMIT {limit}"

            categories_query = """SELECT category FROM categories WHERE id = %s"""

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()

                if results:
                    for row in results:
                        # Get categories from categories table
                        cursor.execute(categories_query, (row[0],))
                        categories = []
                        cat_results = cursor.fetchall()

                        for cat_row in cat_results:
                            categories.append(cat_row[0])

                        # Refer to util/database_setup.py create_tables() for table schemas
                        article = Article(
                            company.upper(), row[1], row[3], row[4], categories, row[5], row[2], retrieved=row[6])

                        articles.append(article)
                else:
                    print(f"no articles on {company} found")
    except Error as e:
        print(e)

    return articles


def get_oldest_date(company: str, connection, category: str = None):
    """Get the publish date of the oldest article stored in the database (of a particular company)

    Args:
        company (str): company
        category (str, optional): category to search for. Defaults to None.

    Returns:
        datetime: date of oldest article
    """
    date = None
    if category:
        query = """SELECT published_date FROM articles a
        JOIN categories c ON a.id = c.id
        JOIN articles_companies ac ON ac.id = a.id
        WHERE category = %s AND company = %s
        ORDER BY a.published_date ASC
        LIMIT 1"""
        params = (category, company)
    else:
        query = """
        SELECT published_date FROM articles a
        JOIN articles_companies ac on ac.id = a.id
        WHERE company = %s 
        ORDER BY published_date ASC
        LIMIT 1"""
        params = (company, )

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
        if results:
            date = results[0][0]

    return date


def get_cache_timestamp(company: str, category: str = None):
    timestamp = None
    with db_connection() as connection:
        print(connection)
        if not category:
            query = """
            SELECT retrieved 
            FROM articles a
            JOIN articles_companies ac ON ac.id = a.id
            WHERE company = %s 
            ORDER BY retrieved DESC LIMIT 1"""
            params = (company, )
        else:
            query = """
            SELECT retrieved 
            FROM articles a 
            JOIN categories c ON a.id = c.id 
            JOIN articles_companies ac ON ac.id = a.id
            WHERE company = %s AND category = %s 
            ORDER BY retrieved DESC LIMIT 1"""
            params = (company, category)

        with connection.cursor() as cursor:
            cursor.execute(query, params=params)
            results = cursor.fetchall()
            if results:
                timestamp = results[0][0]

    return timestamp


def company_exists(company: str):
    """Check if company exists in database

    Args:
        company (str): _description_
    """
    exists = False
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM companies WHERE name = %s", (company, ))
                exists = len(cursor.fetchall()) == 1
    except Error as e:
        print(e)

    return exists


def get_found(company: str, category: str = None):
    """Get the number of 'found' articles in category. If category is none,
    count total

    Args:
        company (str): company name
        category (str, optional): category to search for. Defaults to None.
    """
    found = 0
    try:
        if category:
            params = (company, category)
            query = """SELECT found FROM found WHERE company = %s AND category = %s"""
        else:
            params = (company, )
            query = """SELECT sum(found) FROM found WHERE company = %s"""

        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                if results:
                    found = results[0][0]

    except Error as e:
        print(e)

    return found


def get_all_found(company: str):
    query = """SELECT category, found FROM found WHERE company = %s"""
    found = None
    try:
        with db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (company, ))
                results = cursor.fetchall()
                if results:
                    found = results
                    found = {x[0]: x[1] for x in found}
                    found["all"] = sum(found.values())
    except Error as e:
        print(e)

    return found


def num_articles_in_db(company: str, connection, category: str = None):
    num = 0

    if category:
        query = """
        SELECT count(*) FROM articles
        JOIN categories ON categories.id = articles.id
        JOIN articles_companies ac ON articles.id = ac.id
        WHERE company = %s AND category = %s"""
        params = (company, category)

    else:
        query = """SELECT count(*) FROM articles 
        JOIN articles_companies ac ON articles.id = ac.id
        WHERE company = %s"""
        params = (company,)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()
        if results:
            num = results[0][0]

    return num


def get_page(company: str, page: int, category: str = None):
    """Get articles in page from database. Raises exception if page 
    is not contained in db.

    NOTE: does not check that company exists in database. So if it doesn't nothing will be inserted

    Args:
        company (str): name of company
        page (int): page number (increments of 10)
        category (str, optional): category. Defaults to None.

    Raises:
        Exception: Page is not contained in db

    Returns:
        list[Articles]: list of article objects in page
    """
    page_offset = (page-1)*10
    page_arr = []  # array of articles

    try:
        with db_connection() as connection:
            num_article = num_articles_in_db(company, connection, category)
            db_pages = calculate_pages(num_article)

            if page > db_pages:
                raise pageNotInDatabaseError(
                    f"Company: {company.capitalize()} - Category: {category} - Page: {page} not contained in db.\nDatabase pages: {db_pages}\nCheck 'found' to see if GNEWS has more articles", db_pages)

            elif not category:
                query = """
                SELECT * 
                FROM articles 
                JOIN articles_companies ac on articles.id = ac.id
                WHERE company = %s 
                ORDER BY published_date DESC
                LIMIT 10 OFFSET %s"""
                params = (company, page_offset)

            else:
                query = """
                SELECT * 
                FROM articles a 
                JOIN categories c ON a.id = c.id 
                JOIN articles_companies ac ON a.id = ac.id
                WHERE company = %s AND category = %s
                LIMIT 10 OFFSET %s"""
                params = (company, category, page_offset)

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()

                if result:
                    for row in result:
                        page_arr.append(row_to_article(row, cursor))

    except Error as e:
        print(e)

    return page_arr


def row_to_article(row, cursor):
    """Convert row from 'articles' table into Article object.
    Helper function to help retrieval of articles

    Args:
        row (list): table row
        cursor (MySQLCursorAbstract): SQL cursor

    Returns:
        Article: Article object
    """
    try:
        categories_query = """SELECT category FROM categories WHERE id = %s"""
        name_query = """SELECT company FROM articles_companies WHERE id = %s"""
        # Get categories from categories table
        cursor.execute(categories_query, (row[0],))
        categories = []
        cat_results = cursor.fetchall()

        
        for cat_row in cat_results:
            categories.append(cat_row[0])

        cursor.execute(name_query, (row[0], ))
        name = cursor.fetchall()
        if name:
            name = name[0][0]
        
        # Refer to util/database_setup.py create_tables() for table schemas
        article = Article(name, row[1], row[3], row[4],
                        categories, row[5], row[2], retrieved=row[6])
    except Error as e:
        print(e)
    return article


def search_company_table(search: str):
    """Search for company in database. Returns 5 companies like search string

    Args:
        search (str): _description_

    Returns:
        list: list of company names matching search
    """
    names = []
    print("")
    like = f"%{search}%"
    with db_connection() as connection:
        print(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM companies WHERE name LIKE %s ORDER BY LOCATE(%s, name), name LIMIT 5", (like, search))
            results = cursor.fetchall()
            if results:
                names = [x[0] for x in results]
    return names


def get_company_data(company: str):
    data = None
    try:
        with db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM companies c WHERE c.name = %s", (company, ))
                results = cursor.fetchall()
                if results:
                    cursor.execute(
                        "SELECT industry FROM industries WHERE name = %s", (company, ))
                    industries = [x[0] for x in cursor.fetchall()]
                    data = list(results[0])
                    data.append(industries)

    except Error as e:
        print(e)

    return data
# Update

# Delete

# util


def calculate_pages(num_articles: int):
    if num_articles == 0:
        return 0

    return num_articles//10 + 1

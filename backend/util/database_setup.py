""" 
Thomas De Sa - 2025-06-07
Utility script to create database and table structures as well as populate the
tables with scraped company data. 
"""
import time
from mysql.connector import connect, Error
from config import db_host, db_pass, db_user, db_name
from data_collection import get_fortune_500, get_company_description, get_company_industries, get_aliases, get_company_website
EC_keys = ['labor', 'environment', 'privacy', 'governance', 'diversity', 'human rights', 'consumer safety', 'animal welfare']

def create_tables():
    """
    Creates all tables for database. 
    Will not create tables that already exist. 
    Drop all tables before rebuilding database
    """
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            
            companies_query = """
            CREATE TABLE IF NOT EXISTS companies(
                name varchar(50) PRIMARY KEY, 
                description TEXT,
                website TEXT
                )"""
            industries_query = """
            CREATE TABLE IF NOT EXISTS industries(
                name varchar(50),
                industry varchar (150),
                
                PRIMARY KEY (name, industry),
                FOREIGN KEY (name) REFERENCES companies(name) ON DELETE CASCADE
                )"""
            
            aliases_query = """
            CREATE TABLE IF NOT EXISTS aliases(
                name varchar(50),
                alias varchar(50),
                
                PRIMARY KEY (name, alias),
                FOREIGN KEY (name) REFERENCES companies(name) ON DELETE CASCADE
                )"""
            
            articles_query = """
            CREATE TABLE IF NOT EXISTS articles(
                id SERIAL PRIMARY KEY,
                company_name VARCHAR(50) NOT NULL,
                title TEXT NOT NULL, 
                description TEXT,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                published_date TIMESTAMP,
                retrieved TIMESTAMP NOT NULL,
                
                FOREIGN KEY (company_name) REFERENCES companies(name),
                UNIQUE(url(255))
                )"""
                
            categories_query = """
            CREATE TABLE IF NOT EXISTS categories(
                id BIGINT UNSIGNED NOT NULL,
                category VARCHAR(255) NOT NULL,
                
                PRIMARY KEY (id, category),
                FOREIGN KEY (id) REFERENCES articles(id) ON DELETE CASCADE,
                FOREIGN KEY (category) REFERENCES ethics_categories(category) ON DELETE CASCADE
                )"""
                
            ethics_categories_query = """
            CREATE TABLE IF NOT EXISTS ethics_categories(
                category VARCHAR(255) NOT NULL,
                PRIMARY KEY (category),
                UNIQUE (category)
                )"""
                
            found_query = """
            CREATE TABLE IF NOT EXISTS found(
                company varchar(50),
                category varchar(255),
                found int,
                
                PRIMARY KEY (company, category),
                FOREIGN KEY (company) REFERENCES companies(name) ON DELETE CASCADE,
                FOREIGN KEY (category) REFERENCES ethics_categories(category)
                )"""
                
            with connection.cursor() as cursor:
                cursor.execute(companies_query)
                cursor.execute(ethics_categories_query)
                cursor.execute(industries_query)
                cursor.execute(aliases_query)
                cursor.execute(articles_query)
                cursor.execute(categories_query)
                cursor.execute(found_query)
                
            connection.commit()
            
            print("Tables Created")
    except Error as e:
        print(e)

    return

def populate_companies():
    """
    Inserts name and description of fortune 500 companies into "companies" table. 
    
    misses 8 companies descriptions due to wikidata api being unable to find their sitelink
    based on the name provided by the scrape list.
    
    returns - none"""
    fortune_500 = get_fortune_500()
    with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
        print(connection)

        query = f"""INSERT INTO companies (name,description)
        VALUES (%s, %s)"""
        
        with connection.cursor() as cursor:
            
            for company in fortune_500:
                name = company[1]
                name = name.capitalize()
                description = get_company_description(name)
                #description may be null
                if description: 
                    cursor.execute(query, (name, description))
                
                #don't overwhelm wikipedia
                time.sleep(1)
                
        connection.commit()
    return None

def populate_industries():
    """Populate industries table
    """
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            query = """
            INSERT INTO industries (name, industry)
            VALUES (%s, %s)"""
            
            with connection.cursor() as cursor:
                #Truncate db to avoid duplicates
                cursor.execute("DELETE FROM industries")
                cursor.execute("SELECT name FROM companies")
                results = cursor.fetchall()
                
                for row in results:
                    name = row[0]
                    industries = get_company_industries(name)
                    print(f"{name}: {industries}")

                    if industries:
                        for industry in industries:
                            cursor.execute(query, (name, industry))
                    
            connection.commit()
                    
    except Error as e:
        print(e)
    
    return

def drop_tables():
    """
    WARNING: Drops all tables in database.
    Only use if rebuilding the database.
    """

    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            
            with connection.cursor() as cursor:
                #Drop children first
                cursor.execute("DROP TABLE IF EXISTS industries")
                
                cursor.execute("DROP TABLE IF EXISTS companies")
            connection.commit()
                
    except Error as e:
        print(e)

#TODO update insert_company if new table is created and populated
def insert_company(name: str):
    """Insert company into database.
    
    Insert company into companies table
    Get all industries and insert into industries table

    Args:
        name (str): name of company
    """
    name = name.capitalize()
    inserted = False
    desc = get_company_description(name)
    if desc:
        industries = get_company_industries(name)
        try: 
            website = get_company_website(name)
        except Exception as e:
            print(e)
        try:
            with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
                companies_query = """
                INSERT IGNORE INTO companies (name, description, website)
                VALUE (%s, %s, %s)"""
                industries_query = """
                INSERT IGNORE INTO industries (name, industry)
                VALUES (%s, %s)"""
                
                #Delete the rows if they exists then 
                with connection.cursor() as cursor:
                    cursor.execute(companies_query, (name, desc, website))
                    if industries:
                        for industry in industries:
                            cursor.execute(industries_query, (name, industry))
                connection.commit()
        
        except Error as e:
            print(e)
            
    return inserted 

#TODO populate aliases table possibly...
def insert_alias(name:str):
    
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM companies WHERE name = %s", (name,))
                #If name exists in companies table
                if(len(cursor.fetchall()) == 1):
                    aliases = get_aliases(name)
                    
                    if aliases:
                        for alias in aliases:
                            cursor.execute("INSERT INTO aliases (name, alias) VALUES (%s, %s)", (name, alias))
                else:
                    print(f"{name} could not be found in companies table")    
            connection.commit()        
    except Error as e:
        print(e)

def populate_websites():
    """Populate websites of companies.
    Gets all companies which have a NULL website field then searchs for their website
    """
    try:

        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            search_query = """
            SELECT name FROM companies WHERE website IS NULL"""
            
            update_query = """
            UPDATE companies
            SET website = %s
            WHERE name = %s"""
            with connection.cursor() as cursor:

                cursor.execute(search_query)
                names = [x[0] for x in cursor.fetchall()]
                
                for name in names:
                    try:
                        website = get_company_website(name)
                        print(f"{name}: {website}")
                        if website:
                            cursor.execute(update_query, (website,name))
                        
                        time.sleep(0.5)
                    except Exception as e:
                        print(e)
                        
                connection.commit()

    except Error as e:

        print(e)

def populate_ethics_categories():
    try:
        query = """
        INSERT IGNORE INTO ethics_categories (category) VALUES (%s)"""
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            with connection.cursor() as cursor:
                for category in EC_keys:
                    cursor.execute(query, (category,))
            connection.commit()
    except Error as e:
        print(e)
if __name__ == "__main__":
    #Uncomment this and run script to create database. Will take 20-30 minutes    
    
    # drop_tables()
    # create_tables()
    # populate_companies()
    # populate_websites()
    # populate_industries()
    # populate_ethics_categories()
    pass
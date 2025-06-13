""" 
Thomas De Sa - 2025-06-07
Utility script to create database and table structures as well as populate the
tables with data. 
"""
import time
from mysql.connector import connect, Error
from config import db_host, db_pass, db_user, db_name
from data_collection import get_fortune_500, get_company_description, get_company_industries, get_aliases

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
                description TEXT
                )"""
            industries_query = """
            CREATE TABLE IF NOT EXISTS industries(
                name varchar(50),
                industry varchar (150),
                
                PRIMARY KEY (name, industry),
                FOREIGN KEY (name) REFERENCES companies(name)
                )"""
            
            aliases_query = """
            CREATE TABLE IF NOT EXISTS aliases(
                name varchar(50),
                alias varchar(50),
                
                PRIMARY KEY (name, alias),
                FOREIGN KEY (name) REFERENCES companies(name)
                )"""
            
            with connection.cursor() as cursor:
                cursor.execute(companies_query)
                cursor.execute(industries_query)
                cursor.execute(aliases_query)
                
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
            with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
                companies_query = """
                INSERT INTO companies (name, description)
                VALUE (%s, %s)"""
                industries_query = """
                INSERT INTO industries (name, industry)
                VALUES (%s, %s)"""
                
                with connection.cursor() as cursor:
                    cursor.execute(companies_query, (name, desc))
                    if industries:
                        for industry in industries:
                            cursor.execute(industries_query, (name, industry))
                connection.commit()
        
        except Error as e:
            print(e)
            
    return inserted 

#TODO populate aliases table
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
if __name__ == "__main__":
    #Uncomment this and run script to create database. Will take 20-30 minutes    
    
    # drop_tables()
    # create_tables()
    # populate_companies()
    # populate_industries()
    pass
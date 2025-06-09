""" 
Thomas De Sa - 2025-06-07
Utility script to create database and table structures. 
Run as a module from /backend: `python -m util.database_setup` for import resolutions
"""
import time
from mysql.connector import connect, Error
from config import db_host, db_pass, db_user, db_name
from data_collection import get_fortune_500, get_description

def create_tables():
    """
    Creates all tables for database
    """
    try:
        with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
            print(connection)
            
            companies_query = """CREATE TABLE companies(
            name varchar(50) PRIMARY KEY, 
            description TEXT,
            industry varchar(100)
            )"""
            
            with connection.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS companies")
                cursor.execute(companies_query)
            connection.commit()
            
    except Error as e:
        print(e)

def insert_fortune_500():
    """
    Inserts name, description and industry of fortune 500 companies. 
    It is possible to miss some companies due to timeouts from wikipedia
    
    returns - none"""
    fortune_500 = get_fortune_500()
    with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
        print(connection)
        
        #array will contain companies which failed to get description on
        missed = []
        
        query = f"""INSERT INTO companies (name,description, industry)
        VALUES (%s, %s, %s)"""
        
        with connection.cursor() as cursor:
            
            for company in fortune_500:
                description = get_description(company[1])
                
                if not description:
                    missed.append(company[1])
                else: 
                    cursor.execute(query, (company[1], description, company[2]))
                
                #don't overwhelm wikipedia
                time.sleep(1)
        connection.commit()

    #TODO do something with missed arr
    return None

def insert_names(): 
    """
    Insert names & industry ONLY (no description) of fortune 500 companies
    """
    fortune_500 = get_fortune_500()
    with connect(host=db_host, user=db_user, password=db_pass, database=db_name) as connection:
        print(connection)
        
        query = """INSERT IGNORE INTO companies (name,industry)
        VALUES (%s, %s)"""
        
        with connection.cursor() as cursor:
            for company in fortune_500:
                cursor.execute(query, (company[1], company[2]))
        
        connection.commit()
    
    return


if __name__ == "__main__":
    # create_tables()
    
    # #This will take 15 minutes
    # insert_fortune_500()
    
    insert_names()
    #TODO deal with null descriptions
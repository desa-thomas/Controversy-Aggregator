from datetime import datetime

class Article:
    
    def __init__(self, company: str, headline: str, url: str, source: str, categories: list[str], date_published:datetime, description:str, retrieved = None):
        """Initalize Article object

        Args:
            company (str): Name of company article is about
            headline (str): Headline of article
            url (str): URL of article
            source (str): Name of new outlet which published the article
            categories (list[str]): List of ethical categories that article is categorized into
            date_published (_type_): Date article was published
        """ 
        self.company = company.capitalize()
        self.headline = headline
        self.description = description
        self.url = url
        self.source = source
        self.categories = categories
        self.date_published = date_published
        self.retrieved = retrieved

    def __str__(self):
        s = f"""{"-"*20}
    {self.company} - {self.categories}
    {self.source} - {self.date_published}
    {self.url}

    {self.headline}
        {self.description}
        """
        
        return s 
    
    def __repr__(self):
        s = f"({self.company}, {self.categories}, {self.source}, {self.date_published})"
        return s
    

class pageNotInDatabaseError(Exception):
    def __init__(self, msg, db_pages):
        super().__init__(msg)
        self.db_pages = db_pages
        
class APILimitReached(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        

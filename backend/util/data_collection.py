"""
Thomas De Sa 2025-06-05

Company data collection functions

wikidata API docs: https://www.mediawiki.org/wiki/API:Main_page
Thank you wikidata !
"""

import time
from bs4 import BeautifulSoup
import requests
import re

# For encoding printing error (quick fix)
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_description(company: str):
    """Scrape company description from wikipedia (first paragraph)

    Args:
        company (str): Name of company

    Returns:
        description (str): Description of company
        
        Status_code (int): Status code of request to wikipedia (200, 404, etc)
    """

    description = None
    status_code = None
    url = get_wikipedia_url(company)

    if url:
        try:
            res = requests.get(url, timeout=10)
            print(f"{company} code: {res.status_code}")
            status_code = res.status_code
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")

                content_div = soup.find(
                    "div", {"class": "mw-content-ltr mw-parser-output"})
                description = content_div.find("p", {"class": ""})

                # Paragraph found
                if description is not None:
                    description = description.get_text()

                    # remove citations brackets ([9]) and pronounciation
                    description = re.sub(r'\[\d+\]', '', description)
                    description = re.sub(r'\(([^()]*\/[^()]*?)\)', '', description)
                    description = re.sub(r'\s{2,}', ' ', description).strip()

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch company {company}")
    
    return description, status_code

def get_company_description(company:str):
    """Get a companys description from wikipedia

    Wrapper function of `get_description` that only returns description. Made it so I don't accidently break other stuff lol
    
    Args:
        company (str): name of company

    Returns:
        str: company description
    """
    description, code = get_description(company)
    return description

def get_wikipedia_url(company_name:str, lang="en"):
    """Get wikipedia url using wikidata api. 
    
    Uses the wikidata search api to search for the company then return is corresponding sitelink. 
    Helpful because sometimes the sitelink is different from just /wiki/company_name

    Args:
        company_name (str): name of company
        lang (str, optional): language. Defaults to "en".

    Returns:
        str: url to wikipedia page. None if not found
    """
    wiki_url = None
    
    search_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": company_name,
        "language": lang,
        "format": "json"
    }
    response = requests.get(search_url, params=params).json()
    
    if not response["search"]:
        return None
    
    qid = response["search"][0]["id"]

    #get data using qid
    entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    entity_data = requests.get(entity_url).json()
    sitelinks = entity_data["entities"][qid].get("sitelinks", {})

    wiki_key = f"{lang}wiki"
    
    if wiki_key in sitelinks:
        wiki_url = sitelinks[wiki_key]["url"]
    
    return wiki_url
    

def get_fortune_500():
    """Return 2d array of fotune 500 companies from
    "https://sheet2site.com/api/v3/index.php?key=1S-vhiXvvKFDczI6vAK_dZlGqe3ftxNraArOZIVGivGw&g=1&e=1&e=1"

    Returns:
        fortune_500 (list[list[str]]): 2d array of fortune 500 companies
    """
    fortune_500 = []

    # Iframe from https://www.50pros.com/fortune500
    url = "https://sheet2site.com/api/v3/index.php?key=1S-vhiXvvKFDczI6vAK_dZlGqe3ftxNraArOZIVGivGw&g=1&e=1&e=1"
    res = requests.get(url, timeout=10)
    print(f"code: {res.status_code}")

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "html.parser")
        table = soup.find("tbody")

        for row in table.find_all("tr"):
            row_arr = []
            for td in row.find_all("td"):
                row_arr.append(td.text)

            name = row_arr[1]
            
            #e.g., Labcorp s => Labcorb Holdings
            if name[-2:] == " s": 
                row_arr[1] = name[:-2] + " Holdings"
                
            fortune_500.append(row_arr)

    return fortune_500

def get_aliases(name: str):
    """Get aliases of a company using wikidata API

    Args:
        name (str): name of company

    Returns:
        list[str]: list of aliases
    """
    
    search_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "format": "json"
    }
    
    res = requests.get(search_url, params=params).json()
    #use first result
    entity_id = res["search"][0]["id"]  

    # Step 2: Get full entity data
    entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    entity_data = requests.get(entity_url).json()
    entity = entity_data["entities"][entity_id]

    aliases = [alias["value"] for alias in entity.get("aliases", {}).get("en", [])]

    return aliases



if __name__ == "__main__":
    print(get_aliases("alphabet"))
    pass
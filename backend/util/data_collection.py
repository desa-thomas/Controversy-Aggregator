"""
Thomas De Sa - 2025-06-05

Company data collection functions

wikidata API docs: https://www.mediawiki.org/wiki/API:Main_page
Thank you wikidata !
"""

import time
from bs4 import BeautifulSoup
import requests
import re
from hashlib import md5


# For encoding printing error (quick fix)
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

#Append id.json to url to get entity data
entity_url = "https://www.wikidata.org/wiki/Special:EntityData/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
def get_description(company: str, id = None):
    """Scrape company description from wikipedia (first paragraph)

    Args:
        company (str): Name of company

    Returns:
        description (str): Description of company
        
        Status_code (int): Status code of request to wikipedia (200, 404, etc)
    """

    description = None
    status_code = None
    url = get_wikipedia_url(company,qid= id)

    if url:
        try:
            res = requests.get(url, timeout=10)
            print(f"{company} code: {res.status_code}")
            status_code = res.status_code
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.content, "html.parser")

                content_div = soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
                description = content_div.find("p", {"class": ""},recursive=False)
                
                if not description: 
                    description = content_div.find("p", {"class": ""},recursive=True)
                    
                # Paragraph found
                if description is not None:
                    description = description.get_text().strip()
                    
                    #If wiki page has the coordinates listed first
                    if description[0].isdigit():
                        ps = content_div.find_all("p", {"class": ""},recursive=False)
                        #Edge case if coordinate and desc are in the same <p>
                        if len(ps) == 1:
                            lines = description.split('\n')
                            del lines[0]  # removes second line (index 1)
                            result = '\n'.join(lines)
                            description = result
                        else:
                            description = ps[1]
                            description = description.get_text()
                            

                    # remove citations brackets ([9]) and pronounciation
                    description = re.sub(r'\[\d+\]', '', description)
                    description = re.sub(r'\(([^()]*\/[^()]*?)\)', '', description)
                    description = re.sub(r'\s{2,}', ' ', description).strip()

                    
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch company {company}")
    
    return description, status_code

def get_company_description(company:str, id = None):
    """Get a companys description from wikipedia

    Wrapper function of `get_description` that only returns description. Made it so I don't accidently break other stuff lol
    
    Args:
        company (str): name of company

    Returns:
        str: company description
    """
    description, code = get_description(company, id)
    return description

def get_wikipedia_url(company_name:str, lang="en",qid = None):
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
    if qid is None: 
        qid = get_qid(company_name)
    
    if qid:
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
                row_arr[1] = name[:-2]
                
            fortune_500.append(row_arr)

    return fortune_500

def get_aliases(name: str):
    """Get aliases of a company using wikidata API

    Args:
        name (str): name of company

    Returns:
        list[str]: list of aliases
    """
    
    entity_id = get_qid(name) 

    # Step 2: Get full entity data
    entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    entity_data = requests.get(entity_url).json()
    entity = entity_data["entities"][entity_id]

    aliases = [alias["value"] for alias in entity.get("aliases", {}).get("en", [])]

    return aliases

def get_qid(name:str):
    """Get qid from wikidata api: "https://www.wikidata.org/w/api.php"

    Args:
        name (str): name of company (or otherwise) to get id of
        
    return:
        str: qid of search. None if nothing was found
    """
    
    qid = None
    keywords = ["company", "business", "organization", "conglomerate", "group", "corporation", "platform",
                "firm", "brand", "manufacturer"]
    
    company_suffixs = ["inc", "company", "holdings", "group"]
    
    search_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "format": "json"
    }
    response = requests.get(search_url, params=params).json()
    
    if response["search"]:
        results = response["search"]
        i = 0
        
        while i < len(results) and qid == None:
            item = results[i]
            desc = item.get("description", "").lower()
            label = item.get("label", "").lower()
            
            if any([keyword in desc for keyword in keywords]):
                qid = item["id"]

            elif any([keyword in label for keyword in company_suffixs]):
                qid = item["id"]
            i += 1 
        
        if not qid:
            #If no keyword is found, take the first result
            qid = response["search"][0]["id"]
            print(f"No keyword found in {name}")
    else:
        print(f"{name} search not found")
    
    
    return qid

def get_company_industries(name: str, qid = None):
    """Get list of company's industries from wikidata

    Args:
        name (str): name of company

    Returns:
        list[str]: list of company's industries. None if company could not be found 
    """
    if qid is None:
        qid = get_qid(name)
        
    industries = None
    
    if qid:
        #get data using qid
        entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        entity_data = requests.get(entity_url).json()
        entity = entity_data["entities"][qid]
        claims = entity.get("claims", {})

        #industry is claim "P452" https://www.wikidata.org/wiki/Property:P452
        industries = []
        if "P452" in claims:
            for industry_claim in claims["P452"]:
                try:
                    industry_qid = industry_claim["mainsnak"]["datavalue"]["value"]["id"]
                    industry_entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{industry_qid}.json"
                    industry_entity = requests.get(industry_entity_url).json()
                    industry_label = industry_entity["entities"][industry_qid]["labels"]["en"]["value"]
                    industries.append(industry_label)
                except:
                    continue
        
    if industries: return industries 
    else: return None

def get_company_logo(name: str, id = None):
    """Get logo of company from wikidata

    Args:
        name (str): name of company 

    Returns:
        bytes: logo of company. Returns None if company not found, or wikidata does not have a logo
    """
    if not id:
        id = get_qid(name)
    logo = None
    
    if id:
        entity_data = requests.get(entity_url + f"{id}.json").json()
        entities = entity_data["entities"][id]
        claims = entities.get("claims", {})
        
        if "P154" in claims:
            arr = claims["P154"]
            i = 0
            extension = ""
            extensions = []
            #Make sure file is an svg
            while i < len(arr) and extension != 'svg':
                extension = arr[i]["mainsnak"]["datavalue"]["value"][-3:].strip()
                print(extension)
                extensions.append(extension)
                i+=1 
                
            if extensions[i-1] == "svg":                
                filename = claims["P154"][i-1]["mainsnak"]["datavalue"]["value"]
                print(filename)
                url = get_commons_image_url(filename)

                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    logo = res.content.decode("utf-8")
                else:
                    print(f"Failed to fetch {url}: {res.status_code}")
            
            else:
                print(f"Only type: {extensions} available for {name}")
    return logo 

def get_commons_image_url(filename):
    """Get URL of commons.wikimedia where logo is stored

    Args:
        filename (string): name of file

    Returns:
        _type_: _description_
    """
    name = filename.replace(' ', '_')
    hash_val = md5(name.encode('utf-8')).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{hash_val[0]}/{hash_val[0:2]}/{name}"

def get_company_website(company_name:str, id = None):
    """Get a companies website using wikidata's sparql API

    Args:
        company_name (_type_): _description_

    Raises:
        Exception: 

    Returns:
        str: Website, none if not found
    """    
    website = None
    if not id:
        id = get_qid(company_name)
    
    if id: 
        query = f"""
        SELECT ?website WHERE {{
        wd:{id} wdt:P856 ?website.
        }}
        LIMIT 1
        """
        
        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/sparql-results+json"}

        response = requests.get(url, params={"query": query}, headers=headers)

        if response.ok:
            data = response.json()
            results = data["results"]["bindings"]
            
            if results:
                website = results[0]["website"]["value"]
            
        else:
            raise Exception(f"Query failed: {response.status_code}")

    return website

def get_name(name:str, entity_id=None):
    new_name  = None
    if entity_id is None: 
        entity_id = get_qid(name) 

    if entity_id:
        # Step 2: Get full entity data
        entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
        entity_data = requests.get(entity_url).json()
        entity = entity_data["entities"][entity_id]
        
        new_name = entity["labels"].get("en")["value"]
        
    return new_name
"""
Thomas De Sa 2025-06-05

Company data collection functions"""

import time
from bs4 import BeautifulSoup
import requests
import re

# For encoding printing error (quick fix)
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_description(company: str):
    """Scrape company description from wikipedia (description, logo)

    Args:
        company (str): Name of company

    Returns:
        description (str): descriptioon of company (from wikipedia)
    """

    description = None
    try:
        url = f"https://en.wikipedia.org/wiki/{company}_(company)"
        res = requests.get(url, timeout=10)
        print(f"{company} code: {res.status_code}")

        #If {company}_(company) not found, just search for company
        if res.status_code == 404:
            time.sleep(.5)
            url = f"https://en.wikipedia.org/wiki/{company}"
            res = requests.get(url, timeout=10)
            print(f"{company} code: {res.status_code}")


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
        
    ##TODO
    #get company logo from wiki
    return description


def get_fortune_500():
    """Return 2d array of fotune 500 companies from 
    "https://sheet2site.com/api/v3/index.php?key=1S-vhiXvvKFDczI6vAK_dZlGqe3ftxNraArOZIVGivGw&g=1&e=1&e=1"
    
    Returns:
        fortune_500 (list[list[str]]): 2d array of fortune 500 companies
    """
    fortune_500 = []
    
    #Iframe from https://www.50pros.com/fortune500
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
            
            fortune_500.append(row_arr)

    return fortune_500
if __name__ == "__main__":
    description = get_description("Citi")
    print(description)

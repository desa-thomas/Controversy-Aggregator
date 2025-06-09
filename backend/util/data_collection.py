"""
Thomas De Sa 2025-06-05

Company data collection functions"""

from bs4 import BeautifulSoup
import requests
import re

# For encoding printing error (quick fix)
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_data(company: str):
    """Scrape company data from wikipedia (description, logo, industries)

    Args:
        company (str): Name of company

    Returns:
        _type_: _description_
    """

    description = None
    url = f"https://en.wikipedia.org/wiki/{company}"
    res = requests.get(url)

    print(f"code: {res.status_code}")

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

    return description


def get_fortune_500():
    #IN PROGRESSS
    #FIND OUT WHY THAT LINK DOES NOT GIVE THE TABLE
    url = "https://www.50pros.com/fortune500"
    res = requests.get(url)
    print(f"code: {res.status_code}")

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "html.parser")
        
        print(soup.prettify())
        
        
if __name__ == "__main__":
    # description = get_data("google")d
    # print(description)
    
    get_fortune_500()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled

import re
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://dota2.gamepedia.com/'
API_URL = 'api.php?action=query&list=categorymembers&cmlimit=max' +  \
                                                   '&cmprop=title' + \
                                                   '&format=json' +  \
                                                   '&cmtitle=Category:'
END_URL = 'Lists_of_responses'


def fetch_response_pages():
    """Fetches all available response pages from the Dota Wiki"""
    response_pages = []
    category_json = requests.get(BASE_URL + API_URL + END_URL).json()
    for category in category_json["query"]["categorymembers"]:
        if not 'Announcer' in category["title"]: # Exclude announcer packs
            response_pages.append(BASE_URL + category["title"].replace(" ", "_"))
    return response_pages

def parse_page(page):
    """Returns a page object parsed with BeautifulSoup"""
    return BeautifulSoup(requests.get(page).text, 'html.parser')

def parse_html(html):
    """Returns a html object parsed with BeautifulSoup"""
    return BeautifulSoup(html, 'html.parser')

def create_response_dict(response_pages):
    """Create and returns a dict with all hero responses.
       Example Dict format: { "Axe_Responses": [{"text": "Not so fast!",
                                                "url": "http://hydra-media.cursecdn.com/"
                                                       "dota2.gamepedia.com/d/d2/"
                                                       "Axe_blinkcull_01.mp3"}]}
    """
    response_dict = {}
    for page in response_pages:
        page_name = page.split("/")[-2]
        page_es_check = page.split("/")[-1]
        if (page_es_check == 'es') or (page_name == 'Responses'):
            continue
        print (page_name)

        soup = parse_page(page) # BeautifulSoup object, holding a parsed page

        hero_responses = []
        for li_obj in soup.find_all("li"): # Return all <li> in the page
            if li_obj.a and li_obj.a.has_attr("class") and li_obj.a["class"][0] == "sm2_button":
                response_url = li_obj.a.get('href')
                li_obj.a.extract()
                response_text = li_obj.text.strip()
                hero_responses.append({"text": response_text, "url": response_url})
        response_dict[page_name] = hero_responses
    return response_dict


if __name__ == "__main__":
    print ('start')
    PAGES = fetch_response_pages()
    RESP_DICT = create_response_dict(PAGES)
    json.dump(RESP_DICT, open("newresponses.json", 'w'), indent=3)
    print ('oi')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled
""" Module that find the best game response from a givem text"""

import json
import re
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

def load_response_json(filename):
    """Load a previous created dict from a file"""
    try:
        with open(filename, "r") as response_json:
            response_dict = json.load(response_json)
    except IOError:
        print("Cannot open {}".format(filename))
        return {}

    return response_dict

def matched_strings(string1, string2):
    """Return the number of matched words between two strings"""
    number_of_matches = 0
    for string in string1.split(" "):
        if re.search(r'\b{}\b'.format(string.lower()), string2.lower()) != None:
            number_of_matches += 1
    return number_of_matches


def prepare_responses(query, responses_dict, specific_hero=None):

    best_responses = []
    hero_responses = []
    i = 0
    while i < 10:
        hero, response = find_best_response(query, responses_dict, best_responses, specific_hero)
        if hero != "" and response is not None:
            print ('{0} ++++ {1}'.format(i, response))
            best_responses.append(response)
            hero_responses.append(hero)
            i += 1
        elif response == {}:
            print ('response é none')
            i = 10
        
    return hero_responses, best_responses


def find_best_response(query, responses_dict, best_responses, specific_hero=None):
    """Find the best response from a given query"""

    last_matched = 0
    best_match = -1
    hero_match = ""
    flag = False
    for hero, responses in responses_dict.items():
        if specific_hero is not None:
            if hero.lower().find(specific_hero.lower()) < 0:
                continue
        for idx, response in enumerate(responses):
            matched = matched_strings(query, response["text"])
            if matched > last_matched:
                for resp in best_responses:
                    if response == resp:
                        flag = True
                        break
                if flag:
                    flag = False
                    continue
                best_match = idx
                hero_match = hero
                last_matched = matched
    if hero_match == "" or best_match == -1:
        return "", {}
    else:
        return hero_match, responses_dict[hero_match][best_match]

if __name__ == "__main__":
    print ('start')
    PAGES = fetch_response_pages()
    RESP_DICT = create_response_dict(PAGES)
    json.dump(RESP_DICT, open("newresponses.json", 'w'), indent=3)
    print ('oi')


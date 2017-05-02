#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled
""" Module that find the best game response from a givem text"""

import re
import json

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
    while i < 20:
        hero, response = find_best_response(query, responses_dict, best_responses, specific_hero)
        if hero != "" and response is not None:
            best_responses.append(response)
            hero_responses.append(hero)
            i += 1
        elif response == {}:
            i = 20
        
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


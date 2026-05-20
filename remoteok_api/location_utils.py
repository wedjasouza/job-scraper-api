#!/usr/bin/env python3

"""
This module contains functions to extract location_tokens from the locations
list in the scraped job. It uses the mappings module to map location_tokens
to existing locations so they can be searched.

Functions:
- find_region: Given a country, finds the region corresponding to the country.
- get_continent: If the region is not the name of a continent, get the name of
the continent for the corresponding region.
- format_location: Given a variable list of locations, formats them from
"latin america" to "latin_america" for easier, more standardized searches.
- build_tokens_list: Builds a list of tokens from a location corresponding to
the scraped job. For example: "california" becomes searchable by any of:
["california", "usa", "north_america", "america"].
- flatten: A helper function that flattens a nested list of location_tokens to
a 1D list for easier searching.
- get_location_tokens: Given a list of locations for the scraped job, returns
a list of unique location_tokens for that job for searching purposes.
"""


import re
from remoteok_api.mappings import (
    STATE_MAP,
    REVERSED_STATE_MAP,
    USA_TERMS,
    US_REGION_TOKENS,
    LATIN_AMERICA,
    NORTH_AMERICA,
    SOUTH_AMERICA,
    EUROPE,
    ASIA,
    OCEANIA,
    AFRICA,
    COUNTRIES,
    REGIONS,
    CONTINENTS,
    CITY_TO_COUNTRY
)


def find_region(country: str) -> str:
    """
    Finds and returns the region corresponding to the given country using the
    maps in the mappings module.

    :param country:
        A string representing the country of interest.

    :return:
        A string representing the corresponding region.
    """

    if country in USA_TERMS or country in NORTH_AMERICA:
        return "north_america"
    if country in SOUTH_AMERICA:
        return "south_america"
    if country in EUROPE:
        return "europe"
    if country in OCEANIA:
        return "oceania"
    if country in ASIA["east"]:
        return "east_asia"
    if country in ASIA["west"]:
        return "west_asia"
    if country in ASIA["north"]:
        return "north_asia"
    if country in ASIA["south"]:
        return "south_asia"
    if country in ASIA["central"]:
        return "central_asia"
    if country in AFRICA["east"]:
        return "east_africa"
    if country in AFRICA["west"]:
        return "west_africa"
    if country in AFRICA["north"]:
        return "north_africa"
    if country in AFRICA["south"]:
        return "south_africa"
    if country in AFRICA["central"]:
        return "central_africa"
    return "region_unknown"


def get_continent(region: str) -> str:
    """
    Given a region name, returns the corresponding continent if the region name
    is not the continent. For example, "latin_america" returns "america."

    :param region:
        A string representing the region.

    :return:
        A string representing the continent.
    """

    if "america" in region:
        return "america"
    if "asia" in region:
        return "asia"
    if "africa" in region:
        return "africa"
    return region


def format_location(*args: str) -> str | tuple[str]:
    """
    Given a variable list of locations, formats them from "north america"
    to "north_america" prior to tokenization.

    :param args:
        A list of strings representing the locations.
    :return:
        str: A string representing the location returned if a single
             location is returned.
        tuple[str]: A tuple with a string for each formatted location.
    """

    results = [
        arg.replace(" ", "_")
        for arg in args
    ]

    if len(results) == 1:
        return results[0]

    return tuple(results)


def build_tokens_list(location: list) -> list:
    """
    Given a location, builds a list of tokens for that location. For example:
    "california" becomes searchable by any of: ["california", "usa", "north_america",
    "america"].

    :param location:
        A string representing the location.

    :return:
        A list of tokens (strings) for the given location.
    """

    tokens_list = []

    if location == "not provided":
        tokens_list.append("not provided")
    if location in STATE_MAP:
        location = format_location(location)
        tokens_list.append(location)
        tokens_list.extend(US_REGION_TOKENS)
        return tokens_list
    if location in REVERSED_STATE_MAP:
        location = format_location(REVERSED_STATE_MAP[location])
        tokens_list.append(location)
        tokens_list.extend(US_REGION_TOKENS)
        return tokens_list
    if location in USA_TERMS:
        tokens_list.extend(US_REGION_TOKENS)
        return tokens_list
    if location in COUNTRIES:
        region = find_region(location)
        region, location = format_location(region, location)
        tokens_list.append(location)
        tokens_list.append(region)
        if location in LATIN_AMERICA["north"] or location in LATIN_AMERICA["south"]:
            tokens_list.append("latin_america")
        continent = get_continent(region)
        tokens_list.append(continent)
        return tokens_list
    if location == "latin america":
        location = format_location(location)
        tokens_list.append(location)
        tokens_list.append("america")
        return tokens_list
    if location in REGIONS:
        location = format_location(location)
        tokens_list.append(location)
        continent = get_continent(location)
        tokens_list.append(continent)
        return tokens_list
    if location in CONTINENTS:
        tokens_list.append(location)
        return tokens_list
    if location in CITY_TO_COUNTRY:
        country = CITY_TO_COUNTRY[location]
        region = find_region(country)
        location, country, region = format_location(location, country, region)
        tokens_list.append(location)
        tokens_list.append(region)
        tokens_list.append(country)
        if location in LATIN_AMERICA["north"] or location in LATIN_AMERICA["south"]:
            tokens_list.append("latin_america")
        continent = get_continent(region)
        tokens_list.append(continent)
        return tokens_list
    if location == "worldwide":
        tokens_list.append("worldwide")
        return tokens_list
    return tokens_list


def flatten(nested_list: list) -> list:
    """
    Given a nested list of locations, flattens them into a single
    1D list for easier searching.

    :param nested_list:
        A nested list of locations.

    :return:
        A flattened list of locations.
    """

    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def get_location_tokens(locations: list) -> list:
    """
    Given a list of locations for a scraped job, filters out noise words and returns
    a list of expanded, unique tokens that includes the region and continent of each
    location for easier searching.

    :param locations:
        A list of strings representing the locations.
    :return:
        A list of expanded tokens (strings) for each of the locations.
    """

    location_tokens = []

    noise_words = ["probably", "preferred", "and"]

    for location in locations:
        for word in noise_words:
            pattern = rf'\b{word}\b'
            location = re.sub(pattern, "", location)
            location = re.sub(r"[^a-zA-Z\s]", "", location)
            location = location.strip()
        tokens_list = build_tokens_list(location)
        if tokens_list:
            location_tokens.extend(tokens_list)
            continue
        tokens = re.split(r"[\s,]+", location.lower())
        for token in tokens:
            tokens_list = build_tokens_list(token)
            if tokens_list:
                location_tokens.extend(tokens_list)
                continue
            location_tokens.append(token)

    location_tokens = list(flatten(location_tokens))
    unique_tokens = list(set(location_tokens))
    return unique_tokens

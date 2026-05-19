#!/usr/bin/env python3


"""
Static mappings and token collections used for job parsing and location normalization.

This module contains:
- U.S. state mappings
- Regional location token lists
- Continent lists
- City-to-country map of main tech hubs

These constants are primarily used by map_functions.py to build normalized location
tokens and categorize scraped job data.
"""


# Map full state names to state abbreviations
STATE_MAP = {
    "alabama": "al",
    "alaska": "ak",
    "arizona": "az",
    "arkansas": "ar",
    "california": "ca",
    "colorado": "co",
    "connecticut": "ct",
    "delaware": "de",
    "florida": "fl",
    "georgia": "ga",
    "hawaii": "hi",
    "idaho": "id",
    "illinois": "il",
    "indiana": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kentucky": "ky",
    "louisiana": "la",
    "maine": "me",
    "maryland": "md",
    "massachusetts": "ma",
    "michigan": "mi",
    "minnesota": "mn",
    "mississippi": "ms",
    "missouri": "mo",
    "montana": "mt",
    "nebraska": "ne",
    "nevada": "nv",
    "new hampshire": "nh",
    "new jersey": "nj",
    "new mexico": "nm",
    "new york": "ny",
    "north carolina": "nc",
    "north dakota": "nd",
    "ohio": "oh",
    "oklahoma": "ok",
    "oregon": "or",
    "pennsylvania": "pa",
    "rhode island": "ri",
    "south carolina": "sc",
    "south dakota": "sd",
    "tennessee": "tn",
    "texas": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virginia": "va",
    "washington": "wa",
    "west virginia": "wv",
    "wisconsin": "wi",
    "wyoming": "wy",
    "district of columbia": "dc",
    "puerto rico": "pr"
}


# Map state abbreviations to full state names
REVERSED_STATE_MAP = {v: k for k, v in STATE_MAP.items()}


# set commonly searched USA terms
USA_TERMS = {
    "us",
    "usa",
    "united states",
    "united states of america"
}


# list of US region tokens
US_REGION_TOKENS = ["usa", "north_america", "america"]


# Map of latin american countries by hemisphere
LATIN_AMERICA = {
    "north": [
        "mexico",
        "costa rica",
        "el salvador",
        "guatemala",
        "honduras",
        "nicaragua",
        "panama",
        "cuba",
        "dominican republic",
        "haiti"
    ],
    "south": [
        "argentina",
        "bolivia",
        "brazil",
        "chile",
        "colombia",
        "ecuador",
        "paraguay",
        "peru",
        "uruguay",
        "venezuela"
    ]
}


# List of north american countries
NORTH_AMERICA = [
    "canada",
    "united states",
    "antigua and barbuda",
    "bahamas",
    "barbados",
    "dominica",
    "grenada",
    "jamaica",
    "saint kitts and nevis",
    "saint lucia",
    "saint vincent and the grenadines",
    "trinidad and tobago"
] + LATIN_AMERICA["north"]


# List of south american countries
SOUTH_AMERICA = [
    "guyana",
    "suriname"
] + LATIN_AMERICA["south"]


# List of european countries
EUROPE = [
    "albania",
    "andorra",
    "austria",
    "belarus",
    "belgium",
    "bosnia and herzegovina",
    "bulgaria",
    "croatia",
    "cyprus",
    "czechia",
    "denmark",
    "estonia",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "iceland",
    "italy",
    "kosovo",
    "latvia",
    "liechtenstein",
    "lithuania",
    "luxembourg",
    "malta",
    "moldova",
    "monaco",
    "montenegro",
    "netherlands",
    "north macedonia",
    "norway",
    "poland",
    "portugal",
    "romania",
    "russia",
    "san marino",
    "serbia",
    "slovakia",
    "slovenia",
    "spain",
    "sweden",
    "switzerland",
    "turkey",
    "ukraine",
    "united kingdom",
    "vatican city",
    "georgia"
]


# Map of asian countries by region
ASIA = {
    "east": [
        "china",
        "japan",
        "mongolia",
        "north korea",
        "south korea",
        "taiwan"
    ],
    "west": [
        "armenia",
        "azerbaijan",
        "bahrain",
        "cyprus",
        "georgia",
        "iran",
        "iraq",
        "israel",
        "jordan",
        "kuwait",
        "lebanon",
        "oman",
        "palestine",
        "qatar",
        "saudi arabia",
        "syria",
        "turkey",
        "united arab emirates",
        "yemen"
    ],
    "central": [
        "kazakhstan",
        "kyrgyzstan",
        "tajikistan",
        "turkmenistan",
        "uzbekistan"
    ],
    "north": [
        "russia"
    ],
    "south": [
        "afghanistan",
        "bangladesh",
        "bhutan",
        "india",
        "maldives",
        "nepal",
        "pakistan",
        "sri lanka"
    ]
}


# List of oceania countries
OCEANIA = [
    "new zealand",
    "fiji",
    "solomon islands",
    "vanuatu",
    "kiribati",
    "marshall islands",
    "micronesia",
    "nauru",
    "palau",
    "samoa",
    "tonga",
    "tuvalu",
    "australia",
    "papua new guinea",
    "indonesia"
]


# Map of african countries by region
AFRICA = {
    "north": [
        "algeria",
        "egypt",
        "libya",
        "morocco",
        "sudan",
        "tunisia",
        "western sahara"
    ],
    "west": [
        "benin",
        "burkina faso",
        "cape verde",
        "cote d'ivoire",
        "gambia",
        "ghana",
        "guinea",
        "guinea-bissau",
        "liberia",
        "mali",
        "mauritania",
        "niger",
        "nigeria",
        "senegal",
        "sierra leone",
        "togo"
    ],
    "central": [
        "angola",
        "cameroon",
        "central african republic",
        "chad",
        "democratic republic of the congo",
        "republic of the congo",
        "equatorial guinea",
        "gabon",
        "sao tome and principe"
    ],
    "east": [
        "burundi",
        "comoros",
        "djibouti",
        "eritrea",
        "ethiopia",
        "kenya",
        "madagascar",
        "malawi",
        "mauritius",
        "mozambique",
        "rwanda",
        "seychelles",
        "somalia",
        "south sudan",
        "tanzania",
        "uganda",
        "zambia",
        "zimbabwe"
    ],
    "south": [
        "botswana",
        "eswatini",
        "lesotho",
        "namibia",
        "south africa"
    ]
}


# List of all countries
COUNTRIES = (NORTH_AMERICA +
             SOUTH_AMERICA +
             EUROPE +
             ASIA["east"] +
             ASIA["west"] +
             ASIA["north"] +
             ASIA["south"] +
             ASIA["central"] +
             AFRICA["east"] +
             AFRICA["west"] +
             AFRICA["north"] +
             AFRICA["south"] +
             AFRICA["central"] +
             OCEANIA)


# List of all regions
REGIONS = [
    "north america",
    "south america",
    "europe",
    "east asia",
    "west asia",
    "north asia",
    "south asia",
    "central asia",
    "east africa",
    "west africa",
    "north africa",
    "south africa",
    "west africa",
    "central africa",
    "oceania"
]


# List of continents
CONTINENTS = [
    "america",
    "europe",
    "asia",
    "africa",
    "oceania"
]


# Map of major tech hub cities to their corresponding countries
CITY_TO_COUNTRY = {
    "san francisco": "usa",
    "new york city": "usa",
    "beijing": "china",
    "london": "united kingdom",
    "bangalore": "india",
    "seattle": "usa",
    "shenzhen": "china",
    "tel aviv": "israel",
    "berlin": "germany",
    "austin": "usa",
    "denver": "usa",
    "toronto": "canada",
    "paris": "france",
    "tokyo": "japan",
    "dublin": "ireland",
    "lagos": "nigeria",
    "istanbul": "turkey",
    "pune": "india"
}

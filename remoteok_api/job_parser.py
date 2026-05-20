#!/usr/bin/env python3

"""
This module provides parsing functions for job data processing. It extracts fields,
transforms scraped text, filters jobs, and parses raw HTML/job elements.

Functions:
- extract_title: Extracts job title from a BeautifulSoup Tag object representing
a single job.
- extract_company_name: Extracts job company name from the BeautifulSoup Tag object.
- extract_locations: Extracts job locations and employment types from the BeautifulSoup
Tag object.
- extract_link: Extracts job relative link from the BeautifulSoup Tag object and
attaches it to URL_HOME.
- extract_salary_range: Extracts job salary range from the BeautifulSoup Tag object
if it is available.
- convert_salary_range: Converts the salary range to usable integers and separates
them into min and max values.
- extract_tags: Extracts job tags from the BeautifulSoup Tag object.
- extract_posted_time: Extracts job posting time from the BeautifulSoup Tag object
and converts it to an ISO string.
- parse_job: Combines the above functions to parse an individual job element.
- is_duplicate_slug: Checks if the unique slug has been seen in the current scrape job.
- process_jobs: Processes a batch of jobs provided by scraper.py using the parse_job
function and adds the unique, extracted job_slug to each job. Ensures the job_slug
also does not exist in the current database. Returns the batch of processed jobs to
scraper.py as a list of dictionaries.
"""

import logging
from bs4 import BeautifulSoup, Tag
import emoji
from playwright.sync_api import Locator
from sqlmodel import Session
from remoteok_api.location_utils import get_location_tokens
from remoteok_api.database import get_existing_slugs


URL_HOME = "https://remoteok.com"

EMPLOYMENT_TYPES = {
    "part time",
    "part-time",
    "full time",
    "full-time",
    "contractor",
    "internship",
    "freelance"
}

def extract_title(job: Tag) -> str:
    """
    Extracts job title from a BeautifulSoup Tag object representing
    a single job.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        Job title (string).
    """

    title = job.find("h2", attrs={"itemprop": "title"}).text.strip()
    return title

def extract_company_name(job: Tag) -> str:
    """
    Extracts job company name from the BeautifulSoup Tag object representing
    a single job.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        Job company name (string).
    """

    company_name = job.find("h3", attrs={"itemprop": "name"}).text.strip()
    return company_name

def extract_locations(job: Tag) -> tuple:
    """
    Extracts job locations and employment types from the BeautifulSoup Tag object
    representing a single job.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        A tuple of a list of ob locations and a list of employment types.
    """

    raw_locations = [div.get_text() for div in job.find_all("div", class_="location")]
    locations = []
    employment_types = []
    for item in raw_locations:
        clean_item = emoji.replace_emoji(item, replace="").strip().lower()
        if clean_item in EMPLOYMENT_TYPES:
            employment_types.append(clean_item)
        else:
            locations.append(clean_item)
    locations = [loc for loc in locations if "premium" not in loc]
    if not locations:
        locations = ["not provided"]
    return locations, employment_types

def extract_link(job: Tag) -> str:
    """
    Extracts job relative link from the BeautifulSoup Tag object representing
    a single job and adds it to URL_HOME.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        Job full link (string).
    """

    link = job.find("span", class_="companyLink").get("href")
    link = URL_HOME + link
    return link

def extract_salary_range(job: Tag) -> str | None:
    """
    Extracts job salary range from the BeautifulSoup Tag object representing
    a single job.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        A string with the job salary range in format $90k - $100k.
    """
    salary_range = job.find("div", class_="salary")
    salary_range = salary_range.text if salary_range else None
    salary_range = emoji.replace_emoji(salary_range, replace="").strip() if salary_range else None
    return salary_range

def convert_salary_range(salary_range: str) -> dict | None:
    """
    Strips salary range in the format $90k - $100k of the k's and special characters
    and returns min and max salary in integer form.

    :param salary_range:
        A string of the job salary range.

    :return:
        A dict of min and max salary in integer form.
    """

    if not salary_range:
        return {
            "min": None,
            "max": None,
        }
    if "-" not in salary_range:
        salary = salary_range.strip("$")
        salary = int(float(salary[:-1]) * 1000)
        return {
            "min": salary,
            "max": salary
        }
    salaries = salary_range.split("-")
    for i, salary in enumerate(salaries):
        salaries[i] = salary.strip().strip("$")
        salaries[i] = int(float(salaries[i][:-1]) * 1000)

    return {
        "min": min(salaries),
        "max": max(salaries)
    }

def extract_tags(job: Tag) -> tuple:
    """
    Extracts job tags from the BeautifulSoup Tag object representing
    a single job. Removes tags representing employment types into a
    separate list.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        A tuple of a list of job tags and a list of employment types.
    """

    tags_list = []
    employment_types = []
    tags_container = job.find_all("td", class_="tags")
    if tags_container:
        for container in tags_container:
            tags = container.find_all("h3")
            for tag in tags:
                tag_text = tag.text.lower().strip()
                if tag_text in EMPLOYMENT_TYPES:
                    tag_text = tag_text.replace("-", " ")
                    employment_types.append(tag_text)
                else:
                    tags_list.append(tag_text)
    if not tags_list:
        tags_list = ["No tags available"]
    return tags_list, employment_types

def extract_posted_time(job: Tag) -> str:
    """
    Extracts job posting time from the BeautifulSoup Tag object representing
    a single job.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        An ISO string representing the job posting time.
    """
    posted_time = job.find("time")
    date_string = posted_time["datetime"]
    return date_string


def parse_job(job: Tag) -> dict:
    """
    Combined the above functions to parse an individual job element.

    :param job:
        A BeautifulSoup Tag object.

    :return:
        A dict representing the different keys and values of the parsed job element.
    """

    title = extract_title(job)
    company_name = extract_company_name(job)
    link = extract_link(job)
    locations_and_employment_types = extract_locations(job)
    salary_range = extract_salary_range(job)
    salary = convert_salary_range(salary_range)
    tags = extract_tags(job)
    posted_at = extract_posted_time(job)
    employment_types = locations_and_employment_types[1] + tags[1]
    location_tokens = get_location_tokens(locations_and_employment_types[0])
    if not employment_types:
        employment_types = ["not provided"]
    return {
        "title": title,
        "company_name": company_name,
        "locations": locations_and_employment_types[0],
        "location_tokens": location_tokens,
        "employment_types": employment_types,
        "salary_min": salary["min"],
        "salary_max": salary["max"],
        "tags": tags[0],
        "url": link,
        "posted_at": posted_at
    }

def is_duplicate_slug(slug: str, slugs: set) -> bool:
    """
    Checks whether a slug already exists in the set of slugs already seen in the
    current scrape session.

    :param slug:
        The new individual job slug to check before adding the job.

    :param slugs:
        The set of slugs already seen in the current scrape session.

    :return:
        A boolean value of whether the slug already exists in the set of slugs provided.
    """

    if slug in slugs:
        return True
    return False

def process_jobs(job_elements: list[Locator], seen_slugs: set, session: Session) -> list[dict]:
    """
    Processes a batch of job elements and returns a list of dictionaries.

    Processes a batch of job elements and returns a list of dictionaries representing
    the parsed job elements. Converts Playwright Locators into BeautifulSoup Tags for
    parsing. Ensures individual jobs do not already exist in the database by checking
    individual job slugs. Ensures individual jobs have not been seen or added in the
    current scrape session. Adds slugs to job dictionaries for identification.

    :param job_elements:
        A list of Playwright Locators representing individual job elements.

    :param seen_slugs:
        A set of seen slugs for the current scrape session.

    :param session:
        The database session.

    :return:
        A list of dictionaries representing the parsed job elements to be returned to scraper.py.
    """

    jobs = []
    logging.info("Processing batch...")
    logging.info("Received %s jobs", len(job_elements))
    db_slugs = get_existing_slugs(session)
    for job_element in job_elements:
        html = job_element.evaluate("node => node.outerHTML")
        job_soup = BeautifulSoup(html, "lxml")
        job_tag = job_soup.find("tr")
        slug = job_tag.get("data-slug")
        if not slug:
            continue
        if is_duplicate_slug(slug, seen_slugs):
            continue
        if slug in db_slugs:
            continue
        parsed_job = parse_job(job_tag)
        parsed_job["job_slug"] = slug
        seen_slugs.add(slug)
        jobs.append(parsed_job)
    logging.info("Processed %s jobs", len(jobs))
    return jobs

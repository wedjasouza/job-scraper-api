#!/usr/bin/env python3

"""
Browser automation and scraping logic for RemoteOK job listings.

This module uses Playwright to dynamically load job listings through infinite
scrolling, extract newly visible job rows, parse them into structured dictionaries,
and return unique jobs for database insertion.
"""


import logging
from playwright.sync_api import sync_playwright
from remoteok_api.job_parser import process_jobs


URL_HOME = "https://remoteok.com"


def scrape_jobs_dynamic(url: str, db_path: str, limit: int = 100) -> list[dict]:
    """
    Scrape unique job listings from RemoteOK using Playwright.

    This function launches a Chromium browser session, dynamically scrolls through
    RemoteOK job listings, processes newly visible job elements, filters duplicate
    jobs using session-level slug tracking, and returns up to the requested number
    of unique jobs.

    :param url:
        The RemoteOK URL to scrape.

    :param db_path:
        Path to the SQLite database used for duplicate detection.

    :param limit:
        The maximum number of unique jobs to collect.

    :return:
        A list of dictionaries representing scraped jobs.
    """

    session_seen_slugs = set()

    with sync_playwright() as p:
        logging.info("Scraping %s", url)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector("div.salary")
        logging.info("Requested %s jobs", limit)
        job_elements = page.locator("tr[class*='job']").all()
        jobs = process_jobs(job_elements, session_seen_slugs, db_path)
        previous_count = len(job_elements)
        max_empty_scrolls = 5
        empty_scrolls = 0
        previous_visible_count = 0
        while len(jobs) < limit and empty_scrolls < max_empty_scrolls:
            remaining = limit - len(jobs)
            previous_new_jobs_count = len(jobs)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            job_elements = page.locator("tr[class*='job']").all()
            visible_count = len(job_elements)
            new_elements = job_elements[previous_count:]
            logging.info("Visible elements: %s", len(job_elements))
            new_jobs = process_jobs(new_elements[:remaining], session_seen_slugs, db_path)
            jobs.extend(new_jobs)
            previous_count = len(job_elements)
            if len(jobs) == previous_new_jobs_count and len(jobs) != 0:
                break
            if len(new_jobs) == 0:
                empty_scrolls += 1
            else:
                empty_scrolls = 0
            if visible_count == previous_visible_count:
                empty_scrolls += 1
            previous_visible_count = visible_count

        browser.close()
        logging.info("Collected %s unique jobs", len(jobs))
        return jobs

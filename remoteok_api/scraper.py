#!/usr/bin/env python3

"""
Browser automation and scraping logic for RemoteOK job listings.

This module uses Playwright to dynamically load job listings through infinite
scrolling, extract newly visible job rows, parse them into structured dictionaries,
and return unique jobs for database insertion.
"""


import logging
import time
from typing import Any
from dataclasses import dataclass
from playwright.sync_api import (
    sync_playwright,
    Page,
    Browser,
    Locator,
    TimeoutError as PlaywrightTimeoutError
)
from sqlmodel import Session
from remoteok_api.job_parser import process_jobs


MAX_RETRIES = 3


@dataclass
class ScrollResult:
    """
    Store results from a single scroll iteration.

    :param new_jobs:
        Newly collected jobs from the current scroll.

    :param visible_count:
        Total number of visible job elements after scrolling.
    """

    new_jobs: list[dict[str, Any]]
    visible_count: int


@dataclass
class ScraperState:
    """
    Maintain mutable state during job collection.

    This state object tracks:
    - collected jobs,
    - consecutive empty scrolls,
    - and visible element counts from the previous iteration.

    :param jobs:
        Collected unique job dictionaries.

    :param empty_scrolls:
        Number of consecutive scrolls that produced no meaningful new content.

    :param previous_visible_count:
        Number of visible job elements from the previous scroll iteration.
    """

    jobs: list[dict]
    empty_scrolls: int
    previous_visible_count: int


def load_page(url: str, browser: Browser) -> Page:
    """
    Load a page with retry handling.

    :param url:
        URL to load.

    :param browser:
        Playwright browser instance.

    :return:
        Loaded Playwright page.
    """

    for attempt in range(MAX_RETRIES):

        page = browser.new_page()

        try:
            page.goto(
                url,
                timeout=60000,
                wait_until="domcontentloaded"
            )
            page.wait_for_selector(
                "tr[data-slug]",
                timeout=10000
            )
            return page
        except PlaywrightTimeoutError:
            page.close()
            logging.warning(
                "Attempt %s/%s failed loading %s",
                attempt + 1,
                MAX_RETRIES,
                url
            )

            if attempt == MAX_RETRIES - 1:
                raise

            time.sleep(2)

    raise RuntimeError("Failed to load page")


def extract_job_elements(page: Page) -> list[Locator]:
    """
    Extract job row elements from the loaded RemoteOK page.

    :param page:
        Loaded Playwright page.

    :return:
        List of Playwright locators representing job rows.
    """

    job_elements = page.locator("tr[data-slug]").all()

    if not job_elements:
        raise ValueError("No job elements found on page")

    return job_elements


def scroll_page(page: Page) -> None:
    """
    Scroll the page to trigger lazy loading of additional jobs.

    :param page:
        Loaded Playwright page.

    :return:
        None.
    """

    previous_height = page.evaluate("document.body.scrollHeight")

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    page.wait_for_function(
        f"document.body.scrollHeight > {previous_height}"
    )


def process_scroll_iteration(
        page: Page,
        previous_visible_count: int,
        jobs: list[dict],
        limit: int,
        session_seen_slugs: set[str],
        session: Session,
) -> ScrollResult:
    """
    Process a single scroll iteration and extract new, unique jobs.

    :param page:
        Loaded Playwright page.

    :param previous_visible_count:
        Previous number of visible job elements.

    :param jobs:
        Current collected jobs.

    :param limit:
        Maximum number of unique jobs to collect.

    :param session_seen_slugs:
        Seen job slugs for deduplication.

    :param session:
        The database session.

    :return:
        Tuple containing:
        - New jobs
        - Updated previous count
        - Current visible count
    """

    remaining = limit - len(jobs)
    scroll_page(page)
    job_elements = extract_job_elements(page)
    new_elements = job_elements[previous_visible_count:]
    logging.info("Visible elements: %s", len(job_elements))
    new_jobs = process_jobs(new_elements[:remaining], session_seen_slugs, session)
    return ScrollResult(
        new_jobs,
        len(job_elements)
    )


def update_empty_scrolls(
        new_jobs: list[dict],
        empty_scrolls: int,
        visible_count: int,
        previous_visible_count: int
) -> int:
    """
    Update consecutive empty scroll count.

    A scroll is considered empty when:
    - no new jobs were collected, OR
    - no additional elements became visible

    :param new_jobs:
        Newly collected jobs.

    :param empty_scrolls:
        Current empty scroll count.

    :param visible_count:
        Current visible job count.

    :param previous_visible_count:
        Previous visible job count.

    :return:
        Updated empty scroll count.
    """
    no_new_jobs = not new_jobs
    no_new_elements = (
            visible_count == previous_visible_count
    )

    if no_new_jobs and no_new_elements:
        return empty_scrolls + 1

    return 0


def collect_jobs_until_limit(
        state: ScraperState,
        limit: int,
        max_empty_scrolls: int,
        page: Page,
        session_seen_slugs: set,
        session: Session,
) -> None:
    """
    Continuously scroll and collect jobs until a stopping condition is reached.

    The scrape stops when:
    - the requested job limit is reached, OR
    - the maximum number of consecutive empty scrolls is reached.

    During each iteration:
    - the page is scrolled,
    - newly visible job elements extracted,
    - unseen jobs processed and appended to the scraper state,
    - empty scroll counters updated.

    :param state:
        Mutable scraper state containing collected jobs, scroll counters, and
        scroll metadata.

    :param limit:
        Maximum number of unique jobs to collect.

    :param max_empty_scrolls:
        Maximum allowed consecutive scrolls without meaningful new content.

    :param page:
        Active Playwright page instance.

    :param session_seen_slugs:
        Set of job slugs already processed during the session.

    :param session:
        The database session.
    """

    while len(state.jobs) < limit and state.empty_scrolls < max_empty_scrolls:
        previous_new_jobs_count = len(state.jobs)
        scroll_result = process_scroll_iteration(
            page,
            state.previous_visible_count,
            state.jobs,
            limit,
            session_seen_slugs,
            session
        )
        state.jobs.extend(scroll_result.new_jobs)
        if state.jobs and len(state.jobs) == previous_new_jobs_count:
            break
        state.empty_scrolls = update_empty_scrolls(
            scroll_result.new_jobs,
            state.empty_scrolls,
            scroll_result.visible_count,
            state.previous_visible_count
        )
        state.previous_visible_count = scroll_result.visible_count


def scrape_jobs_dynamic(url: str, session: Session, limit: int = 100) -> list[dict]:
    """
    Scrape unique job listings from RemoteOK using Playwright.

    This function launches a Chromium browser session, dynamically scrolls through
    RemoteOK job listings, processes newly visible job elements, filters duplicate
    jobs using session-level slug tracking, and returns up to the requested number
    of unique jobs.

    :param url:
        The RemoteOK URL to scrape.

    :param session:
        The database session.

    :param limit:
        The maximum number of unique jobs to collect.

    :return:
        A list of dictionaries representing scraped jobs.
    """

    session_seen_slugs = set()

    with sync_playwright() as p:
        logging.info("Scraping %s", url)
        browser = p.chromium.launch(headless=True)
        try:
            page = load_page(url, browser)
            logging.info("Requested %s jobs", limit)
            job_elements = extract_job_elements(page)
            jobs = process_jobs(job_elements, session_seen_slugs, session)
            max_empty_scrolls = 5
            empty_scrolls = 0
            previous_visible_count = len(job_elements)
            state = ScraperState(jobs, empty_scrolls, previous_visible_count)
            collect_jobs_until_limit(
                state,
                limit,
                max_empty_scrolls,
                page,
                session_seen_slugs,
                session
            )
            logging.info("Collected %s unique jobs", len(state.jobs))
            return state.jobs
        finally:
            browser.close()

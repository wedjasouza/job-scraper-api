#!/usr/bin/env python3

"""
Command-line interface for the RemoteOK scraper.

This module parses command-line arguments, configures logging, runs the scraping
pipeline, and stores scraped jobs in a SQLite database.
"""


import argparse
import logging
from sqlmodel import Session
from remoteok_api.scraper import scrape_jobs_dynamic
from remoteok_api.database import create_tables, insert_jobs, engine


parser = argparse.ArgumentParser(description="Scrape jobs from remoteok.com and upload to database")


parser.add_argument("-v", "--verbose", action = "store_true", help = "Enable verbose output")
parser.add_argument("--limit", type = int, default = 100,
                    help = "The number of fresh/unseen jobs to scrape")


args = parser.parse_args()


# enable verbose output
if args.verbose:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


URL_HOME = "https://remoteok.com"


def main() -> None:
    """
    Run the job scraping pipeline.

    This function reads command-line arguments, creates database table if it
    does not exist, scrapes job listings from RemoteOK, and inserts the collected
    jobs into the database.

    :return:
        None.
    """
    limit = args.limit
    create_tables()
    with Session(engine) as session:
        jobs = scrape_jobs_dynamic(URL_HOME, session, limit)
        insert_jobs(jobs, session)


if __name__ == "__main__":
    main()

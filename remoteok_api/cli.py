#!/usr/bin/env python3

"""
Command-line interface for the RemoteOK scraper.

This module parses command-line arguments, configures logging, runs the scraping
pipeline, and stores scraped jobs in a SQLite database.
"""


import argparse
import logging
from pathlib import Path
from remoteok_api.scraper import scrape_jobs_dynamic
from remoteok_api.database import create_table, insert_jobs


parser = argparse.ArgumentParser(description="Scrape jobs from remoteok.com and upload to database")


parser.add_argument("-v", "--verbose", action = "store_true", help = "Enable verbose output")
parser.add_argument("--db", dest="db", type = str, default="outputs/jobs.db",
                    help = "The output database path")
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

    This function reads command-line arguments, normalizes the database filename,
    creates the SQLite database table if it does not already exist, scrapes job
    listings from RemoteOK, and inserts the collected jobs into the database.

    :return:
        None.
    """
    limit = args.limit
    db = args.db
    if not db.endswith(".db"):
        db += ".db"
    db_path = Path(db)
    create_table(db_path)
    jobs = scrape_jobs_dynamic(URL_HOME, db_path, limit)
    insert_jobs(jobs, db_path)


if __name__ == "__main__":
    main()

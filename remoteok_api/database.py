#!/usr/bin/env python3

"""
This module provides functions for creating the database and table, inserting jobs
from a list of jobs to the database, and obtaining existing slugs in the database
to ensure duplicate rows are not inserted.

Functions:
- create_table: Creates the table in the database, ensuring that the database and
Path exist.
- insert_jobs: Inserts the scraped jobs to the database table.
- get_existing_slugs: Retrieves the existing slugs from the database.
"""


import sqlite3
import json
from pathlib import Path


def create_table(db_path: Path) -> None:
    """
    This function creates a table, ensuring that the table exists and that
    the path exists.

    :param db_path:
        The Path to the database.

    :return:
        None.
    """

    db_path.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_slug TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            url TEXT NOT NULL,
            posted_at TEXT NOT NULL,
            salary_min INTEGER,
            salary_max INTEGER,
            locations TEXT,
            location_tokens TEXT,
            employment_types TEXT,
            tags TEXT
        )
    """)
    connection.commit()
    cursor.close()


def insert_jobs(jobs: list[dict], db_path: Path) -> None:
    """
    Insert scraped job dictionaries into a SQLite database.

    This function processes a list of job dictionaries, converts list-based
    fields into JSON strings for storage, normalizes optional fields such as
    salary and employment types, and inserts each job into the database
    specified by db_path.

    :param jobs:
        A list of dictionaries representing scraped jobs.

    :param db_path:
        Path to a SQLite database file.

    :return:
        None
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    for job in jobs:
        tags = json.dumps(job["tags"])
        if job["employment_types"]:
            employment_types = json.dumps(job["employment_types"])
        else:
            employment_types = None
        locations = json.dumps(job["locations"])
        location_tokens = json.dumps(job["location_tokens"])
        if job["salary"]:
            salary_min = job["salary"]["min"]
            salary_max = job["salary"]["max"]
        else:
            salary_min = None
            salary_max = None
        job_slug = job["job_slug"]
        title = job["title"]
        company_name = job["company_name"]
        url = job["url"]
        posted_at = job["posted_at"]
        job_tuple = (job_slug, title, company_name, url,
                     posted_at, salary_min, salary_max,
                     locations, location_tokens, employment_types,
                     tags)
        cursor.execute("""INSERT OR IGNORE INTO jobs (job_slug, title,
        company_name, url, posted_at, salary_min, salary_max, locations, location_tokens,
        employment_types, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", job_tuple)
    connection.commit()
    connection.close()


def get_existing_slugs(db_path: Path) -> set[str]:
    """
    This function returns a list of existing job slugs from the database.

    :param db_path:
        Path to a SQLite database file.

    :return:
        Set of existing job slugs.
    """
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        query = """
            SELECT job_slug FROM jobs
        """
        cursor.execute(query)
        slugs = cursor.fetchall()
    return {slug[0] for slug in slugs}

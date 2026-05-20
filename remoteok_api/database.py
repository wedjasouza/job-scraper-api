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


import os
from collections.abc import Generator
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel, select
from remoteok_api.models import Job


# load environment variables
load_dotenv()

# Get database from environment variable
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


def create_tables() -> None:
    """
    Create database tables if they do not already exist.
    """

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Create and yield a database session.
    """

    with Session(engine) as session:
        yield session


def insert_jobs(jobs: list[dict], session: Session) -> None:
    """
    Insert scraped job dictionaries into the database

    :param jobs:
        List of scraped job dictionaries.

    :param session:
        Database session.

    :return:
        None
    """

    job_models = [Job(**job_data) for job_data in jobs]

    try:
        session.add_all(job_models)
        session.commit()
    except Exception:
        session.rollback()
        raise


def get_existing_slugs(session: Session) -> set[str]:
    """
    Return a set of existing job slugs from the database.

    :param session:
        Database session.

    :return:
        Set of existing job slugs.
    """

    statement = select(Job.job_slug)

    slugs = session.exec(statement).all()

    return set(slugs)

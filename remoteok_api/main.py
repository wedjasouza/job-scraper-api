#!/usr/bin/env python3

"""
FastAPI application for querying scraped RemoteOK jobs.

This module defines API endpoints for retrieving, filtering, and analyzing job
listings stored in the SQLite database. It also provides summary statistics and
filtering utilities for remote job searches.
"""


import heapq
import os
from typing import Annotated
from datetime import datetime, timedelta, UTC
from collections import Counter
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlmodel import select, create_engine, Session
from sqlalchemy import func
from dotenv import load_dotenv
from remoteok_api.models import Job, StatsModel
from remoteok_api.database import get_session


# load environment variables
load_dotenv()


# Get database from environment variable
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


# short location term conversions
SHORT_LOCATION_TERMS = {
    "us": "usa",
    "uk": "united kingdom"
}

app = FastAPI()


@app.get("/jobs/", response_model=list[Job])
def get_jobs(session: Session = Depends(get_session)) ->list[Job]:
    """
    Lists all jobs in the database.

    :return:
        A list of Job objects.
    """
    jobs = session.exec(select(Job)).all()
    return jobs


@app.get("/jobs/search", response_model=list[Job])
def search_jobs(
        q: str | None = None,
        days: int | None = None,
        location: Annotated[list[str] | None, Query()] = None,
        employment_type: Annotated[list[str] | None, Query()] = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        tag: Annotated[list[str] | None,  Query()] = None,
        sort_by: str | None = None,
        include_worldwide: bool | None = None,
        session: Session = Depends(get_session)
) -> list[Job]:
    """
    Retrieve filtered job listings from the database.

    This endpoint supports filtering by query terms, location, salary, employment
    type, tags, and posting age. It also supports sorting by date or salary.

    :return:
        A list of matching job listings.
    """
    jobs = session.exec(select(Job)).all()

    filtered_jobs = []

    for job in jobs:

        matches_query = True
        matches_location = True
        matches_salary = True
        matches_tags = True
        matches_employment_type = True
        matches_days = True
        matches_worldwide = True

        if q:
            matches_query = (
                q.lower() in job.title.lower()
                or q.lower() in job.company_name.lower()
                or q.lower() in job.tags
            )

        if days:
            cutoff = datetime.now(UTC) - timedelta(days=days)

            matches_days = job.posted_at >= cutoff

        if location:

            matches_location = False


            for requested_location in location:
                requested_location = requested_location.lower()

                requested_location = SHORT_LOCATION_TERMS.get(
                    requested_location,
                    requested_location
                )

                if " " in requested_location:
                    requested_location = requested_location.replace(" ", "_")

                if requested_location in job.location_tokens:
                    matches_location = True
                    continue

        if salary_min:
            matches_salary = (
                job.salary_max is not None
                and job.salary_max >= salary_min
            )

        if salary_max:
            matches_salary = (
                matches_salary
                and job.salary_min is not None
                and job.salary_min <= salary_max
            )

        if tag:
            matches_tags = any(
                requested_tag.lower() in job.tags
                for requested_tag in tag
            )

        if employment_type:
            matches_employment_type = any(
                requested_employment_type.lower() in job.employment_types
                for requested_employment_type in employment_type
            )

        if include_worldwide:
            matches_worldwide = any(
                "worldwide" in location.lower()
                for location in job.location_tokens
            )

        location_match = matches_location

        if include_worldwide:
            location_match = matches_location or matches_worldwide

        if (
            matches_query
            and location_match
            and matches_salary
            and matches_tags
            and matches_employment_type
            and matches_days
        ):
            filtered_jobs.append(job)

    if sort_by:
        if sort_by == "salary":
            filtered_jobs.sort(
                key=lambda job: job.salary_max or 0,
                reverse=True
            )
        elif sort_by == "date":
            filtered_jobs.sort(
                key=lambda job: job.posted_at,
                reverse=True
            )


    return filtered_jobs


@app.get("/jobs/tags/{tag}", response_model=list[Job])
def get_jobs_by_tag(
        tag: str,
        session: Session = Depends(get_session)
) -> list[Job]:
    """
    Retrieves a list of jobs matching the given tag from the database.

    :return:
        A list of Job objects.
    """
    jobs = session.exec(select(Job).filter(Job.tags.contains(tag))).all()
    if not jobs:
        raise HTTPException(status_code=404, detail=f"No jobs found matching tag {tag}")
    return jobs


@app.get("/jobs/{job_slug}", response_model=Job)
def get_job(
        job_slug: str,
        session: Session = Depends(get_session)
) -> Job:
    """
    Retrieves a single job by its slug.

    :return:
        A Job object.
    """
    job = session.get(Job, job_slug)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs/stats/", response_model=StatsModel)
def get_stats(
        session: Session = Depends(get_session)
) -> StatsModel:
    """
    Retrieve summary statistics for stored jobs.

    Returns aggregate metrics including total jobs, recent jobs, remote jobs, salary
    availability, and top job tags.

    :return:
        A dictionary containing database statistics.
    """

    total_count = session.scalar(select(func.count()).select_from(Job))

    cutoff = datetime.now(UTC) - timedelta(days=7)

    recent_jobs_statement = (select(func.count())
                             .select_from(Job)
                             .where(Job.posted_at >= cutoff))

    recent_jobs = session.execute(recent_jobs_statement).scalar()

    salary_statement = (select(func.count())
                        .select_from(Job)
                        .where(Job.salary_min.is_not(None)))

    with_salary = session.execute(salary_statement).scalar()

    remote_statement = (select(func.count())
                        .select_from(Job)
                        .where(Job.location_tokens.contains(["remote"])))

    remote = session.execute(remote_statement).scalar()

    tags_statement = select(Job.tags).where(Job.tags is not None)

    tags = session.execute(tags_statement).scalars().all()

    tags_lists = list(tags)

    flat_list = [tag for tag_list in tags_lists for tag in tag_list]

    counts = Counter(flat_list)

    top_3_tags = heapq.nlargest(3, counts, key=counts.get)

    stats = StatsModel(
        total=total_count,
        recent=recent_jobs,
        with_salary=with_salary,
        remote=remote,
        top_tags=top_3_tags,
    )

    return stats

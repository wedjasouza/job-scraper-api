#!/usr/bin/env python3

"""
This module contains classes that define the table schema in the PostgreSQL
database and the statistical model used by main.py to return job statistics.
"""

from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel


class Job(SQLModel, table=True):
    """
    Represents a remote job listing stored in the PostgreSQL database.

    This model defines the schema for the jobs table and is used by FastAPI as
    both a database ORM model and API response model.
    """

    __tablename__ = "jobs"

    job_slug: str = Field(primary_key=True, sa_column_kwargs={'autoincrement': False})
    title: str
    company_name: str
    url: str
    posted_at: datetime
    salary_min: int | None = None
    salary_max: int | None = None
    locations: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    location_tokens: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    employment_types: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))


class StatsModel(BaseModel):
    """
    Represents aggregate statistics about stored job listings.

    Used by the statistics endpoint to return summary information such as total
    jobs, recent jobs, salary availability, remote status, and popular tags.
    """

    total: int
    recent: int | None
    with_salary: int | None
    remote: int | None
    top_tags: list[str]

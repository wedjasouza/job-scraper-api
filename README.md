# RemoteOK Job Scraper API

A Python job scraping and search API built with Playwright, BeautifulSoup,
FastAPI, SQLModel, and PostgreSQL.

This project scrapes remote job listings from RemoteOK, stores them in a
PostgreSQL database, and exposes a searchable REST API.

## Features

- Dynamic job scraping with Playwright
- PostgreSQL database support
- SQLModel ORM integration
- FastAPI REST API
- Job search filtering
- Salary filtering
- Location filtering
- Employment type filtering
- Duplicate prevention using job slugs
- Configurable database path
- CLI support

---

## Tech Stack

- Python
- FastAPI
- SQLModel
- SQLAlchemy
- PostgreSQL
- Playwright
- BeautifulSoup4

---

## Installation

Clone the repository:

```bash
git clone https://github.com/wedjasouza/job-scraper-api.git

cd job-scraper-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

### Windows

```bash
.venv\Scripts\activate
```

### Mac/Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install
```

## PostgreSQL Setup

This project uses PostgreSQL for persistent job storage.

Install PostgreSQL locally and create a database:

```sql
CREATE DATABASE remoteok_jobs;
```

Create a `.env` file in the project root directory:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/remoteok_jobs
```

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:mypassword@localhost:5432/remoteok_jobs
```

The application automatically creates required tables on startup.

---

### PostgreSQL Connection Format

```text
postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

Example components:

| Component | Example |
|---|---|
| USERNAME | postgres |
| PASSWORD | mypassword |
| HOST | localhost |
| PORT | 5432 |
| DATABASE_NAME | remoteok_jobs |

---

### Verify PostgreSQL Is Running

Test your connection with:

```bash
psql -U postgres -d remoteok_jobs
```
---

## Project Structure

```text
job-scraper-api/
│
├── remoteok_api/
│   ├── cli.py
│   ├── database.py
│   ├── scraper.py
│   ├── job_parser.py
│   ├── map_functions.py
│   ├── mappings.py
│   ├── models.py
│   └── main.py
│
├── .env
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Usage

### Scrape Jobs

Scrape 100 jobs into the database:

```bash
python -m remoteok_api.cli
```

Specify a scrape limit:

```bash
python -m remoteok_api.cli --limit 50
```

Enable verbose logging:

```bash
python -m remoteok_api.cli --verbose
```

---

## Running the API

Start the FastAPI server:

```bash
uvicorn remoteok_api.main:app --reload
```

---

## API Endpoints

### Search Jobs

```http
GET /jobs/search
```

Supported query parameters:

- `q`
- `days`
- `location`
- `employment_type`
- `salary_min`
- `salary_max`
- `tag`
- `sort_by`
- `include_worldwide`

Example:

```http
GET /jobs/search?q=python&location=usa&salary_min=100000
```

---

## Example Response

```json
[
  {
    "job_slug": "senior-python-engineer",
    "title": "Senior Python Engineer",
    "company_name": "Example Company",
    "salary_min": 120000,
    "salary_max": 160000,
    "locations": ["usa"],
    "employment_types": ["full time"],
    "tags": ["python", "fastapi"]
  }
]
```

---

## Notes

- Job listings are scraped dynamically from RemoteOK.
- Duplicate jobs are prevented using unique job slugs.
- SQLite databases are automatically created if they do not exist.

---

## Future Improvements

- Retry handling for Playwright
- PostgreSQL support
- Docker support
- Async scraping
- Background scheduled scraping
- Pagination
- Authentication

---

## License

MIT License
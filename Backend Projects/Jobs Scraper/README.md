# Startup.com Jobs Scraper

A Python-based backend project that scrapes job listings from [startup.jobs](https://startup.jobs), extracts detailed job data, and stores it into a MySQL database. This scraper uses Selenium with `undetected_chromedriver` to avoid bot detection and interact with dynamic content.

---

## Features

- Search jobs by **title** and **location**
- Extracts job title, company, location, salary, job type, full description, and link
- Stores data into a **MySQL** database
- Handles pagination using the "Show more results" button
- Skips duplicates using unique job link
- Uses environment variables to secure DB credentials


---

## Tech Stack

- **Language**: Python
- **Scraping**: Selenium + undetected-chromedriver
- **Database**: MySQL
- **Environment Handling**: `python-dotenv`

---

## Requirements

Install dependencies via pip:

```bash
pip install selenium undetected-chromedriver mysql-connector-python python-dotenv

import os 
import time
import random
import urllib.parse
import mysql.connector
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# MySQL setup
load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE")
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        salary TEXT,
        job_type TEXT,
        description TEXT,
        link VARCHAR(700) UNIQUE
    )
""")
conn.commit()

# Load already stored job links
cursor.execute("SELECT link FROM jobs")
existing_links = set(row[0] for row in cursor.fetchall())

# User input
job_query = input("Enter job title: ").strip()
location_query = input("Enter location: ").strip()
encoded_job = urllib.parse.quote_plus(job_query)
encoded_location = urllib.parse.quote_plus(location_query)
search_url = f"https://startup.jobs/?since=24h&q={encoded_job}&loc={encoded_location}"

# Selenium setup with undetected-chromedriver
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

driver = uc.Chrome(options=chrome_options)

print(f"🔗 Navigating to: {search_url}")
driver.get(search_url)

def extract_description_same_tab(link):
    try:
        time.sleep(random.uniform(0.5, 1.5))
        driver.get(link)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.post__content"))
        )
        description_element = driver.find_element(By.CSS_SELECTOR, "div.post__content")
        description = description_element.text.strip()
    except Exception as e:
        print(f"    Failed to get description from {link}: {e}")
        description = "N/A"
    return description

def extract_jobs_from_page():
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-search-target="hits"] > div.isolate')
    except Exception as e:
        print(f" Error finding job cards: {e}")
        return 0

    print(f" Found {len(job_cards)} job cards.")
    new_jobs = 0
    job_info_list = []

    for card in job_cards:
        title = company = location = salary = job_type = link = "N/A"
        try:
            link_elem = card.find_element(By.CSS_SELECTOR, 'a[data-mark-visited-links-target="anchor"]')
            href = link_elem.get_attribute("href")
            link = "https://startup.jobs" + href if not href.startswith("http") else href
            if link in existing_links:
                continue

            try:
                title = card.find_element(By.CSS_SELECTOR, 'div.sm\\:truncate').text.strip()
            except:
                pass
            try:
                company = card.find_element(By.CSS_SELECTOR, 'a[href^="/company/"]').text.strip()
            except:
                pass
            try:
                extracted_location = card.find_element(By.CSS_SELECTOR, 'div[data-post-template-target="location"]').text.strip()
                location = extracted_location if extracted_location else "N/A"
            except:
                pass

            job_info_list.append((title, company, location, salary, job_type, link))
        except Exception as e:
            print(f"     Card extraction error: {e}")

    for title, company, location, salary, job_type, link in job_info_list:
        try:
            description = extract_description_same_tab(link)
            cursor.execute('''
                INSERT INTO jobs (title, company, location, salary, job_type, description, link)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (title, company, location, salary, job_type, description, link))
            conn.commit()

            existing_links.add(link)
            new_jobs += 1
            print(f"    ✔️ Stored: {title[:50]} (Company: {company}, Location: {location})")
            driver.back()
            time.sleep(random.uniform(1, 2))
        except mysql.connector.Error as err:
            conn.rollback()
            if err.errno == 1062:
                print(f"     Duplicate: {title[:50]}")
            else:
                print(f"     DB Error: {err}")
        except Exception as e:
            print(f"     Storage error: {e}")

    return new_jobs

def get_page_info():
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        body = driver.find_element(By.TAG_NAME, "body")
        current = int(body.get_attribute("data-search-current-page-value") or 1)
        total = int(body.get_attribute("data-search-total-pages-value") or 1)
        return current, total
    except Exception as e:
        print(f" Page info error: {e}")
        return -1, -1

def click_show_more(current_page_before_click):
    try:
        # Wait for the "Show more results" link to be clickable
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-search-target='nextPage']"))
        )
        
        # Scroll to the button to ensure visibility before clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(0.3)  # slight wait helps with rendering delays

        # Click the "Show more results" link
        button.click()

        # Wait for the page number to increase after click
        WebDriverWait(driver, 12).until(
            lambda d: int(d.find_element(By.TAG_NAME, "body")
                         .get_attribute("data-search-current-page-value") or 0) > current_page_before_click
        )

        return True

    except TimeoutException:
        print(" 'Show more results' not clickable or no more pages.")
        return False

    except Exception as e:
        print(f" Pagination error: {e}")
        return False


# Main scraping loop
total_jobs = 0
current_page, total_pages = get_page_info()
print(f" Starting on page {current_page} of {total_pages}")

total_jobs += extract_jobs_from_page()

retries = 0
max_retries = 3

while current_page < total_pages:
    time.sleep(random.uniform(0.5, 1))
    print(f"\n Page {current_page + 1}")

    if not click_show_more(current_page):
        if retries < max_retries:
            print(" Retrying pagination...")
            retries += 1
            continue
        else:
            print(" Stopping after max retries.")
            break

    retries = 0
    current_page, _ = get_page_info()
    total_jobs += extract_jobs_from_page()

# Cleanup
time.sleep(1)
driver.quit()
cursor.close()
conn.close()
print("✅ Done. Total new jobs scraped:", total_jobs)
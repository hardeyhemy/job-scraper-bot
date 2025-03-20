import requests
import os
import time

# Load environment variables
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Apify Scraper Actor ID (Replace with your actual ID)
ACTOR_ID = "x7rTUsENpdiuhe1aO"
APIFY_RUN_URL = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_API_KEY}"

# Start Apify Scraper
run_response = requests.post(APIFY_RUN_URL, json={})
run_data = run_response.json()

if "data" in run_data and "id" in run_data["data"]:
    run_id = run_data["data"]["id"]
    print(f"Apify Scraper started! Run ID: {run_id}")
else:
    print("Failed to start Apify Scraper")
    exit()

# Wait for job to complete
MAX_WAIT_TIME = 300  # 5 minutes
INTERVAL = 15
elapsed_time = 0

while elapsed_time < MAX_WAIT_TIME:
    run_status = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}").json()
    status = run_status.get("data", {}).get("status", "")

    if status == "SUCCEEDED":
        print("Scraping completed!")
        break

    print(f"Waiting... ({elapsed_time}/{MAX_WAIT_TIME} sec)")
    time.sleep(INTERVAL)
    elapsed_time += INTERVAL

# Fetch scraped job data
DATASET_ID = run_data.get("data", {}).get("defaultDatasetId", None)
if not DATASET_ID:
    print("Failed to get dataset ID.")
    exit()

JOBS_URL = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?token={APIFY_API_KEY}"
jobs_response = requests.get(JOBS_URL)
jobs = jobs_response.json()

# Send jobs to Telegram
if jobs:
    message = "📢 *New Job Listings*\n\n"
    for job in jobs[:10]:  # Send up to 10 jobs
        job_title = job.get("title", "No title")
        job_link = job.get("url", "#")
        message += f"🔹 [{job_title}]({job_link})\n"

    TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    requests.post(TELEGRAM_URL, json=payload)
    print("Jobs sent to Telegram!")
else:
    print("No jobs found.")

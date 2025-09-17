import requests
from bs4 import BeautifulSoup

# Config
URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Student&locationHierarchy1=2fcb99c455831013ea52bbe14cf9326c"  # replace with student jobs page
BOT_TOKEN = "***REMOVED***"
CHAT_ID = "***REMOVED***"

def get_jobs():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    with open("jobs.txt", "w") as f:
        f.write("\n".join(soup.prettify().splitlines()))
    jobs = soup.find_all("a", class_="css-1142bqn")  # Workday job links usually have a similar class
    return [job.text.strip() for job in jobs]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def main():
    # Load previous jobs (if any)
    try:
        with open("jobs.txt", "r") as f:
            old_jobs = set(f.read().splitlines())
    except FileNotFoundError:
        old_jobs = set()

    # Get current jobs
    new_jobs = set(get_jobs())

    # Find newly posted jobs
    diff = new_jobs - old_jobs
    if diff:
        for job in diff:
            send_telegram(f"New NVIDIA job posted: {job}\n{URL}")

    # Save current jobs
    with open("jobs.txt", "w") as f:
        f.write("\n".join(new_jobs))

if __name__ == "__main__":
    main()

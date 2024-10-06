from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests
import re
from datetime import date

app = FastAPI()

# Helper Functions

def parse_job(job_response) -> dict:
    job_soup = BeautifulSoup(job_response.text, "html.parser")
    
    try:
        company_name = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
        description = job_soup.find("div", {"class": "description__text description__text--rich"}).text.strip()
        location = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
        date_posted = job_soup.find("span", {"class": "posted-time-ago__text topcard__flavor--metadata"}).text.strip()
        scrapping_date = str(date.today())

        return {
            "company_name": company_name,
            "location": location,
            "date_posted": date_posted,
            "description": description,
            "scrapping_date": scrapping_date
        }
    except AttributeError:
        return None  # Return None if any field is missing

@app.get("/job")
async def get_job_data(job_id: str):
    if not job_id:
        raise HTTPException(status_code=400, detail="JOB_ID parameter is required.")

    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    job_response = requests.get(job_url, headers={'User-agent': 'Mozilla/5.0'})

    if job_response.status_code == 200:
        job_data = parse_job(job_response)
        if job_data:
            print("yes")
            return JSONResponse(content={"status": "success", "data": job_data}, status_code=200)
        else:
            print("no")
            raise HTTPException(status_code=500, detail="Job data could not be parsed.")
    else:
        print("fuck")
        raise HTTPException(status_code=job_response.status_code, detail="Failed to fetch job data.")

import csv
import pandas as pd
from jobspy import scrape_jobs
import datetime
import os

OUTPUT_FILE = 'README.md'

def fetch_jobs():
    print("Fetching jobs...")
    
    # Define search criteria
    search_terms = ["Software Engineer", "Site Reliability Engineer", "Cloud Engineer", "Data Engineer"]
    locations = ["Washington, DC", "San Francisco, CA"]
    
    all_jobs = pd.DataFrame()

    for location in locations:
        for term in search_terms:
            print(f"Searching for {term} in {location}...")
            try:
                jobs = scrape_jobs(
                    site_name = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter", "monster", "careerbuilder", "simplyhired", "flexjobs", "dice", "usajobs"],
                    search_term=term,
                    location=location,
                    results_wanted=10,
                    hours_old=168, # Last 7 days
                    country_watchlist=["USA"]
                )
                if not jobs.empty:
                    jobs['search_term'] = term
                    jobs['search_location'] = location
                    all_jobs = pd.concat([all_jobs, jobs], ignore_index=True)
            except Exception as e:
                print(f"Error fetching {term} in {location}: {e}")

    return all_jobs

def generate_markdown(jobs_df):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    md = f"# Tech Jobs Aggregator\n\n"
    md += f"Automated job listings for DC and SF (Last 7 days). Last updated: {now}\n\n"

    if jobs_df.empty:
        md += "No jobs found in the last run.\n"
        return md

    # Clean up data
    if 'date_posted' in jobs_df.columns:
        jobs_df['date_posted'] = pd.to_datetime(jobs_df['date_posted']).dt.date
    else:
        jobs_df['date_posted'] = 'N/A'

    # Group by Location and Role
    locations = jobs_df['search_location'].unique()
    
    for location in locations:
        md += f"## {location}\n\n"
        loc_jobs = jobs_df[jobs_df['search_location'] == location]
        
        roles = loc_jobs['search_term'].unique()
        for role in roles:
            md += f"### {role}\n\n"
            role_jobs = loc_jobs[loc_jobs['search_term'] == role]
            
            # Deduplicate by job_url
            role_jobs = role_jobs.drop_duplicates(subset=['job_url'])
            
            for _, job in role_jobs.iterrows():
                title = job.get('title', 'N/A')
                company = job.get('company', 'N/A')
                url = job.get('job_url', '#')
                date = job.get('date_posted', 'N/A')
                site = job.get('site', 'N/A')
                
                md += f"- [{title}]({url}) - **{company}** ({site}) - *{date}*\n"
            
            md += "\n"

    return md

def main():
    jobs = fetch_jobs()
    markdown_content = generate_markdown(jobs)
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(markdown_content)
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

import sqlite3

# Function to create the database and tables
def create_database():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    # Create companies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        logo_url TEXT,
        career_page_url TEXT
    )
    """)

    # Create job_descriptions table with company_id as a foreign key
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        skills TEXT,
        experience TEXT,
        projects TEXT,
        education TEXT,
        qualifications TEXT,
        company_id INTEGER,
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )
    """)

    conn.commit()
    conn.close()

# Function to insert a company into the companies table
def insert_company(name, logo_url, career_page_url):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO companies (name, logo_url, career_page_url)
    VALUES (?, ?, ?)""", (name, logo_url, career_page_url))
    conn.commit()
    conn.close()

# Function to insert a job into the job_descriptions table
def insert_job(title, description, skills, experience, projects, education, qualifications, company_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO job_descriptions (title, description, skills, experience, projects, education, qualifications, company_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (title, description, skills, experience, projects, education, qualifications, company_id))
    conn.commit()
    conn.close()

# Function to fetch all jobs with company details
def fetch_jobs():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT j.title, j.description, j.skills, j.experience, j.projects, j.education, j.qualifications, c.name, c.logo_url, c.career_page_url
    FROM job_descriptions j
    JOIN companies c ON j.company_id = c.id
    """)
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Main function to set up the database and insert sample data
if __name__ == "__main__":
    # Create the database and tables
    create_database()

    # Insert sample companies
    companies = [
        ("Google", "https://logo.clearbit.com/google.com", "https://careers.google.com"),
        ("Amazon", "https://logo.clearbit.com/amazon.com", "https://www.amazon.jobs"),
        ("Microsoft", "https://logo.clearbit.com/microsoft.com", "https://careers.microsoft.com"),
        ("Apple", "https://logo.clearbit.com/apple.com", "https://www.apple.com/careers"),
        ("Meta", "https://logo.clearbit.com/meta.com", "https://www.metacareers.com"),
        ("Tesla", "https://logo.clearbit.com/tesla.com", "https://www.tesla.com/careers"),
        ("Netflix", "https://logo.clearbit.com/netflix.com", "https://jobs.netflix.com"),
        ("IBM", "https://logo.clearbit.com/ibm.com", "https://www.ibm.com/careers"),
        ("Intel", "https://logo.clearbit.com/intel.com", "https://www.intel.com/content/www/us/en/jobs/jobs-at-intel.html"),
        ("Oracle", "https://logo.clearbit.com/oracle.com", "https://www.oracle.com/careers")
    ]

    for company in companies:
        insert_company(*company)

    # Fetch company IDs for job insertion
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM companies")
    company_ids = {name: id for id, name in cursor.fetchall()}
    conn.close()

    # Insert sample job descriptions with company IDs
    job_list = [
        ("Software Engineer", 
         "Develop, test, and maintain software applications using Python and JavaScript.",
         "Python, JavaScript, React, SQL",
         "2+ years in software development",
         "Built an e-commerce platform, developed REST APIs",
         "Bachelor’s in Computer Science",
         "Certified in Full-Stack Development",
         company_ids["Google"]),
        
        ("Data Scientist",
         "Analyze data, build predictive models, and use machine learning techniques.",
         "Python, Machine Learning, SQL, Data Visualization",
         "3+ years in data science",
         "Developed fraud detection system, predictive analytics for sales forecasting",
         "Master’s in Data Science",
         "Google Data Analytics Certification",
         company_ids["Amazon"]),

        ("Project Manager",
         "Manage project timelines, coordinate teams, and ensure timely delivery of products.",
         "Project Management, Agile, Scrum, Leadership",
         "5+ years in project management",
         "Managed software development projects, cloud migration projects",
         "MBA in Project Management",
         "PMP Certification",
         company_ids["Microsoft"]),

        ("Cybersecurity Analyst",
         "Monitor and secure IT systems, prevent cyber threats, and perform penetration testing.",
         "Cybersecurity, Ethical Hacking, SIEM, Firewalls",
         "3+ years in cybersecurity",
         "Implemented security measures for a financial institution",
         "Bachelor’s in Cybersecurity or related field",
         "Certified Ethical Hacker (CEH)",
         company_ids["Apple"]),

        ("Cloud Engineer",
         "Design, deploy, and manage cloud infrastructure using AWS, Azure, or GCP.",
         "AWS, Azure, Docker, Kubernetes, Terraform",
         "3+ years in cloud computing",
         "Migrated enterprise applications to AWS cloud",
         "Bachelor’s in Computer Science",
         "AWS Solutions Architect Certification",
         company_ids["Meta"])
    ]

    for job in job_list:
        insert_job(*job)
    
    print("Database setup complete with companies and job roles!")

    
    jobs = fetch_jobs()
    for job in jobs:
        title, description, skills, experience, projects, education, qualifications, company_name, logo_url, career_page_url = job
        print(f"Title: {title}")
        print(f"Company: {company_name}")
        print(f"Logo: {logo_url}")
        print(f"Career Page: {career_page_url}")
        print(f"Description: {description}")
        print(f"Skills: {skills}")
        print(f"Experience: {experience}")
        print(f"Projects: {projects}")
        print(f"Education: {education}")
        print(f"Qualifications: {qualifications}")
        print("-" * 50)

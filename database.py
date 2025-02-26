import sqlite3

def create_database():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        skills TEXT,
        experience TEXT,
        projects TEXT,
        education TEXT,
        qualifications TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_job(title, description, skills, experience, projects, education, qualifications):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO job_descriptions (title, description, skills, experience, projects, education, qualifications)
    VALUES (?, ?, ?, ?, ?, ?, ?)""", (title, description, skills, experience, projects, education, qualifications))
    
    conn.commit()
    conn.close()

def fetch_jobs():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, skills, experience, projects, education, qualifications FROM job_descriptions")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Run this once to create the database and insert sample data
if __name__ == "__main__":
    create_database()
    
    # Insert sample job descriptions with detailed requirements
    job_list = [
        ("Software Engineer", 
         "Develop, test, and maintain software applications using Python and JavaScript.",
         "Python, JavaScript, React, SQL",
         "2+ years in software development",
         "Built an e-commerce platform, developed REST APIs",
         "Bachelor’s in Computer Science",
         "Certified in Full-Stack Development"),
        
        ("Data Scientist",
         "Analyze data, build predictive models, and use machine learning techniques.",
         "Python, Machine Learning, SQL, Data Visualization",
         "3+ years in data science",
         "Developed fraud detection system, predictive analytics for sales forecasting",
         "Master’s in Data Science",
         "Google Data Analytics Certification"),

        ("Project Manager",
         "Manage project timelines, coordinate teams, and ensure timely delivery of products.",
         "Project Management, Agile, Scrum, Leadership",
         "5+ years in project management",
         "Managed software development projects, cloud migration projects",
         "MBA in Project Management",
         "PMP Certification"),

        ("Cybersecurity Analyst",
         "Monitor and secure IT systems, prevent cyber threats, and perform penetration testing.",
         "Cybersecurity, Ethical Hacking, SIEM, Firewalls",
         "3+ years in cybersecurity",
         "Implemented security measures for a financial institution",
         "Bachelor’s in Cybersecurity or related field",
         "Certified Ethical Hacker (CEH)"),

        ("Cloud Engineer",
         "Design, deploy, and manage cloud infrastructure using AWS, Azure, or GCP.",
         "AWS, Azure, Docker, Kubernetes, Terraform",
         "3+ years in cloud computing",
         "Migrated enterprise applications to AWS cloud",
         "Bachelor’s in Computer Science",
         "AWS Solutions Architect Certification"),

        ("AI/ML Engineer",
         "Develop and deploy AI and machine learning models for automation and analytics.",
         "Python, TensorFlow, PyTorch, NLP, Deep Learning",
         "3+ years in AI/ML",
         "Built AI-powered chatbots and image recognition models",
         "Master’s in AI/ML or related field",
         "Deep Learning Specialization (Coursera)"),

        ("Financial Analyst",
         "Analyze financial data, create reports, and provide investment recommendations.",
         "Excel, Financial Modeling, SQL, Power BI",
         "2+ years in finance",
         "Developed budget forecasts for a multinational company",
         "Bachelor’s in Finance or Accounting",
         "CFA Level 1 Certification"),

        ("Digital Marketing Specialist",
         "Plan and execute online marketing campaigns, SEO, and content strategies.",
         "SEO, Google Ads, Social Media Marketing, Content Strategy",
         "2+ years in digital marketing",
         "Managed social media and PPC ads for an e-commerce brand",
         "Bachelor’s in Marketing or Business",
         "Google Ads Certification"),

        ("UX/UI Designer",
         "Design user-friendly interfaces and improve user experience for websites and apps.",
         "Figma, Adobe XD, UX Research, Prototyping",
         "2+ years in UI/UX design",
         "Designed a mobile app UI for a startup",
         "Bachelor’s in Design or Computer Science",
         "UX Design Certification (Google)"),

        ("Mechanical Engineer",
         "Design, develop, and maintain mechanical systems and products.",
         "CAD, SolidWorks, MATLAB, Thermodynamics",
         "3+ years in mechanical engineering",
         "Developed an energy-efficient HVAC system",
         "Bachelor’s in Mechanical Engineering",
         "Certified SolidWorks Professional (CSWP)"),

        ("Civil Engineer",
         "Plan and oversee construction projects, ensuring structural integrity and compliance.",
         "AutoCAD, Structural Analysis, Project Management",
         "5+ years in civil engineering",
         "Managed construction of commercial buildings",
         "Bachelor’s in Civil Engineering",
         "PE License (Professional Engineer)"),

        ("Nurse Practitioner",
         "Provide primary and specialized healthcare, diagnose illnesses, and prescribe treatments.",
         "Patient Care, EHR Systems, Diagnostics, Medication Management",
         "4+ years in nursing",
         "Worked in ICU and emergency care units",
         "Master’s in Nursing",
         "Board Certified Family Nurse Practitioner (FNP)"),

        ("Pharmacist",
         "Dispense medications, provide drug therapy counseling, and manage pharmacy operations.",
         "Pharmacology, Prescription Management, Drug Safety",
         "2+ years in pharmacy",
         "Managed pharmacy inventory and provided consultations",
         "Doctor of Pharmacy (PharmD)",
         "Licensed Pharmacist (State Board Exam)"),

        ("Human Resources Manager",
         "Oversee recruitment, employee relations, and organizational development.",
         "HR Management, Employee Relations, Payroll, Training",
         "5+ years in HR",
         "Implemented company-wide training and performance management programs",
         "Bachelor’s in Human Resources or Business",
         "SHRM Certified Professional (SHRM-CP)")
    ]

    # Insert all job roles into the database
    for job in job_list:
        insert_job(*job)
    
    print("Database setup complete with multiple job roles!")

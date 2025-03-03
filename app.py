from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask, jsonify, request, render_template, redirect, url_for, session,send_file,send_from_directory,flash
from bson import ObjectId
import base64
import pymongo 
import numpy as np
from datetime import datetime
import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as PlatypusImage
import re
import PyPDF2
import spacy
nlp = spacy.load("en_core_web_sm")
import re
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('DEBUG', default=False)
from io import BytesIO
from PIL import Image
import base64
import gridfs
from bson import ObjectId
from datetime import timedelta
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session expires after 30 minutes
from pymongo import MongoClient
client = MongoClient(os.getenv('MONGO_URI'))
@app.before_request
def before_request():
    session.permanent = True  




RESUME_UPLOAD_FOLDER = 'static/resume_uploads/'
app.config['RESUME_UPLOAD_FOLDER'] = RESUME_UPLOAD_FOLDER

# Ensure the directory exists
os.makedirs(RESUME_UPLOAD_FOLDER, exist_ok=True)
db = client['face_recognition']
collection = db['users'] 
admin_collection=db["admins"]
job_applications_collection = db['job_applications']
fs = gridfs.GridFS(db) 
secret_key = os.urandom(24)
print(secret_key)
app.secret_key = secret_key

REGISTRATION_UPLOAD_FOLDER = 'static/registration_uploads/'
app.config['REGISTRATION_UPLOAD_FOLDER'] = REGISTRATION_UPLOAD_FOLDER

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ADMIN_UPLOAD_FOLDER = 'static/admin_uploads' 
app.config['ADMIN_UPLOAD_FOLDER'] = ADMIN_UPLOAD_FOLDER 

ADMIN_LOGIN_UPLOAD_FOLDER = 'static/admin_login_uploads' 
app.config['ADMIN_LOGIN_UPLOAD_FOLDER'] = ADMIN_LOGIN_UPLOAD_FOLDER 

ATTEND_UPLOAD_FOLDER = 'static/attendance_uploads' 
app.config['ATTEND_UPLOAD_FOLDER'] = ATTEND_UPLOAD_FOLDER 


EDIT_UPLOAD_FOLDER = 'static/edit_uploads'
app.config['EDIT_UPLOAD_FOLDER'] = EDIT_UPLOAD_FOLDER
def get_jobs_from_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description ,skills FROM job_descriptions")
    jobs = [{"title": row[0], "description": row[1], "skills": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jobs
@app.route("/")
def index():
    jobs=get_jobs_from_db()
    return render_template("index.html",jobs=jobs)

@app.route("/get_jobs", methods=["GET"])
def get_jobs():
    jobs = get_jobs_from_db()
    return jsonify(jobs)
@app.route("/resume")
def resume():
    return render_template("resume.html")


@app.route("/admin_register", methods=['GET'])
def admin_register_page():
    return render_template("admin_register.html")
@app.route("/admin_register", methods=["POST"])
def admin_register():
    name = request.form.get("name")
    password = request.form.get("password")
    photo = request.files["photo"]

    if not name or not password or not photo:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    # Upload photo to Cloudinary
    cloudinary_response = cloudinary.uploader.upload(photo)
    photo_url = cloudinary_response['secure_url']

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Save admin data to the database
    admin_data = {
        "name": name,
        "password": hashed_password,
        "photo_url": photo_url,
        "role": "admin"
    }
    admin_collection.insert_one(admin_data)
    session['admin_name'] = name
    session['admin_role'] = 'admin'

    return jsonify({"success": True, "message": "Admin registration successful"})
@app.route("/admin_login", methods=["POST"])
def admin_login():
    
    name = request.form.get("name")
    password = request.form.get("password")
    print(name)
    print(password)

    if not name or not password:
        return jsonify({"success": False, "error": "Name and password are required"}), 400

    # Find the admin in the database
    admin = admin_collection.find_one({"name": name})
    if not admin:
        return jsonify({"success": False, "error": "Admin not found"}), 404

    # Verify the password
    if not check_password_hash(admin.get("password", ""), password):
        return jsonify({"success": False, "error": "Incorrect password"}), 401

    # Set session for the logged-in admin
    session['admin_name'] = admin['name']
    session['admin_role'] = 'admin'  # Add role for clarity
    return jsonify({"success": True, "name": admin['name']})

@app.route("/admin_login", methods=['GET'])
def admin_login_page():
    return render_template("admin_login.html")


@app.route("/admin")
def admin():
    # Check if the session is for an admin
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return redirect(url_for('admin_login_page'))

    # Fetch all users from the database
    users = list(collection.find({}, {"_id": 1, "name": 1, "rollno": 1, "branch": 1, 
                                      "registration_no": 1, "bio": 1, "photo_url": 1, 
                                      "ats_score": 1, "missing_skills": 1, "recommended_jobs": 1}))
    
    return render_template("admin.html", user=users)




@app.route("/user_register", methods=['GET'])
def user_register():
    return render_template('register.html')

@app.route("/register", methods=["POST"])
def register():
    try:
        # Debug: Log incoming form data
        print("Incoming form data:", request.form)
        print("Incoming files:", request.files)

        # Extract form data
        user_name = request.form.get("user_name")
        name = request.form.get("name")
        rollno = request.form.get("rollno")
        registration_no = request.form.get("registrationno")
        branch = request.form.get("branch")
        bio = request.form.get("bio")
        photo = request.files.get('photo')  # Use .get() to avoid KeyError if 'photo' is missing
        password = request.form.get("password")

        # Validate required fields
        if not user_name or not name or not rollno or not registration_no or not branch or not bio or not photo or not password:
            return jsonify({"success": False, "error": "All fields are required"}), 400

        # Debug: Log photo file details
        print("Photo file:", photo.filename, photo.content_type)

        # Upload photo to Cloudinary
        try:
            cloudinary_response = cloudinary.uploader.upload(photo)
            photo_url = cloudinary_response['secure_url']
            print("Cloudinary response:", cloudinary_response)
        except Exception as e:
            print("Cloudinary upload failed:", str(e))
            return jsonify({"success": False, "error": "Failed to upload photo to Cloudinary"}), 500

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create user data
        user_data = {
            "user_name": user_name,
            "name": name,
            "rollno": int(rollno),
            "registration_no": int(registration_no),
            "branch": branch,
            "bio": bio,
            "photo_url": photo_url,  # Use Cloudinary URL
            "password": hashed_password,
            "role": "user"
        }

        # Debug: Log user data
        print("User data to insert:", user_data)

        # Insert user data into MongoDB
        try:
            collection.insert_one(user_data)
            print("User data inserted successfully")
        except pymongo.errors.DuplicateKeyError as e:
            print("Duplicate key error:", str(e))
            return jsonify({"success": False, "error": "User name already exists"}), 400
        except Exception as e:
            print("MongoDB insertion failed:", str(e))
            return jsonify({"success": False, "error": "Failed to insert user data into MongoDB"}), 500

        # Set user session
        session['user_name'] = user_name
        session['user_role'] = 'user'

        # Return success response
        return jsonify({"success": True, 'name': name})

    except Exception as e:
        # Handle any other exceptions
        error_message = f"An unexpected error occurred: {str(e)}"
        print(error_message)
        return jsonify({"success": False, "error": error_message}), 500
@app.route("/delete_user/<user_id>", methods=['POST'])
def delete_user(user_id):
    # Check if the session is for an admin
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return redirect(url_for('admin_login_page'))

    collection.delete_one({"_id": ObjectId(user_id)})
    return redirect(url_for('admin'))
@app.route("/edit_user/<user_id>", methods=['GET', 'POST'])
def edit_user(user_id):
    # Check if the session is for an admin
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return redirect(url_for('admin_login_page'))

    # Fetch the user from the database
    user = collection.find_one({"_id": ObjectId(user_id)})
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get("name")
        rollno = request.form.get("rollno")
        branch = request.form.get("branch")
        registrationno = request.form.get("registrationno")
        bio = request.form.get("bio")
        photo = request.files.get('photo')

        # Handle photo upload
        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            photo_url = photo_path
        else:
            photo_url = user['photo_url']

        # Validate and convert rollno and registrationno to integers
        try:
            rollno = int(rollno)
            registrationno = int(registrationno)
        except ValueError:
            return jsonify({"success": False, "error": "rollno and registration_no must be integers"}), 400

        # Update the user's details in the database
        collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "name": name,
                "rollno": rollno,
                "branch": branch,
                "registration_no": registrationno,
                "bio": bio,
                "photo_url": photo_url,
                "role": "user"
            }}
        )

        # Redirect to the admin dashboard after updating the user
        return redirect(url_for('admin'))

    # Render the edit user form with the user's current data
    return render_template('edit_user.html', user=user)
@app.route('/user_login')
def user_login():
    return render_template('login.html')
@app.route("/login", methods=["POST"])
def login():
    user_name = request.form.get("user_name")
    password = request.form.get("password")
    

    if not user_name or not password:
        return jsonify({"success": False, "error": "Name and password are required"}), 400

    # Find the user in the database
    user = collection.find_one({"user_name": user_name})
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    # Verify the password
    if not check_password_hash(user.get("password", ""), password):
        return jsonify({"success": False, "error": "Incorrect password"}), 401

    # Set session for the logged-in user
    session['user_name'] = user['user_name']
    session['user_role'] = 'user'  # Add role for clarity
    return jsonify({"success": True, "user_name": user['user_name']})
@app.route("/success")
def success():
    # Check if the session is for a user
    if 'user_name' not in session or session.get('user_role') != 'user':
        return redirect(url_for('user_login'))
    jobs=get_jobs_from_db()
    user_name = session['user_name']
    user = collection.find_one({"user_name": user_name})
    job_applications = list(job_applications_collection.find({"user_name": user_name}))

    # Add job applications to the user object
    user['application_status'] = job_applications
    return render_template("success.html", user=user,jobs=jobs)

@app.route("/admin_success")
def admin_success():
    # Check if the session is for an admin
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return redirect(url_for('admin_login_page'))

    # Fetch the user's details from the database
    user_name = request.args.get("user_name")
    user = collection.find_one({"user_name": user_name})

    if not user:
        return redirect(url_for('user_login'))
    
  # Redirect to login if user not found

    return render_template("success.html", user=user)

@app.route("/logout")
def logout():
    # Clear user session keys
    session.pop('user_name', None)
    session.pop('user_role', None)
    return redirect(url_for('index'))

@app.route("/admin_logout")
def admin_logout():
    # Clear user session keys
    session.pop('admin_name', None)
    session.pop('admin_role', None)
    return redirect(url_for('index'))
GENERATED_UPLOAD_FOLDER = 'static/generated_uploads/'
app.config['GENERATED_UPLOAD_FOLDER'] = GENERATED_UPLOAD_FOLDER
os.makedirs(GENERATED_UPLOAD_FOLDER, exist_ok=True)

UPDATE_UPLOAD_FOLDER = 'static/update_uploads/'
app.config['UPDATE_UPLOAD_FOLDER'] = UPDATE_UPLOAD_FOLDER
os.makedirs(UPDATE_UPLOAD_FOLDER, exist_ok=True)

RESUME_FOLDER = 'static/resume_uploads/'
os.makedirs(RESUME_FOLDER, exist_ok=True)
app.config['RESUME_FOLDER'] =RESUME_FOLDER


nlp = spacy.load("en_core_web_sm")  # Load NLP model
def fetch_admin_jobs():
    """Fetches job descriptions and skills from the database."""
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions")
    jobs = cursor.fetchall()
    conn.close()
    return jobs
# Fetch job descriptions from the database
def fetch_jobs():
    """Fetches job descriptions and skills from the database."""
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, skills FROM job_descriptions")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

SOFTWARE_SKILLS = {
    'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
    'html', 'css', 'react', 'angular', 'vue', 'django', 'flask', 'node.js', 
    'git', 'docker', 'kubernetes', 'aws', 'azure', 'sql', 'mongodb', 'postgresql',
    'machine learning', 'deep learning', 'data analysis', 'artificial intelligence',
    'rest api', 'graphql', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
    'numpy', 'linux', 'agile', 'scrum', 'devops', 'cybersecurity', 'blockchain',
    'big data', 'hadoop', 'spark', 'nosql', 'oop', 'functional programming',
    'unit testing', 'ci/cd', 'microservices', 'serverless', 'redux', 'typescript',
    'spring boot', '.net', 'laravel', 'rails', 'express.js', 'keras', 'ansible',
    'terraform', 'jenkins', 'golang', 'rust', 'elasticsearch', 'rabbitmq', 'kafka'
}
def extract_skills(text):
    """Extracts software-related skills from text using NLP and predefined patterns"""
    doc = nlp(text.lower())  # Process text in lowercase for consistent matching
    skills = set()

    # Check noun chunks for multi-word skills
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.replace(' ', '_')  # Format multi-word phrases
        if chunk_text in SOFTWARE_SKILLS:
            skills.add(chunk_text.replace('_', ' '))
    
    # Check individual tokens
    for token in doc:
        # Consider nouns, proper nouns, and adjectives (which might be part of technical terms)
        if token.pos_ in ["NOUN", "PROPN", "ADJ"]:
            # Check lemma form and text form
            lemma = token.lemma_.lower()
            if lemma in SOFTWARE_SKILLS or token.text.lower() in SOFTWARE_SKILLS:
                skills.add(token.text.lower())
    
    # Additional pattern matching for version numbers and special cases
    for match in re.finditer(r'\b(?:python|java|c\+\+|c#|\.net)\s*\d*\.?\d+\b', text.lower()):
        skills.add(match.group().strip())
    
    # Handle common variations
    variations_map = {
        'js': 'javascript',
        'node': 'nodejs',
        'reactjs': 'react',
        'vuejs': 'vue',
        'angularjs': 'angular',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'aws cloud': 'aws',
        "sql":"mysql"
    }
    
    for variation, standard in variations_map.items():
        if variation in skills:
            skills.remove(variation)
            skills.add(standard)
    
    return skills
# Extract skills from job descriptions


def calculate_ats_score(resume_text, job_description, resume_skills, job_skills):
    """Calculates ATS score using text similarity and skill matching."""
    # Convert resume_skills and job_skills to sets
    resume_skills_set = set(resume_skills)
    job_skills_set = set(job_skills)

    # Calculate text similarity using TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer().fit_transform([resume_text, job_description])
    similarity_score = cosine_similarity(vectorizer[0], vectorizer[1])[0][0] * 100

    # Calculate skill match score
    matched_skills = resume_skills_set.intersection(job_skills_set)
    skill_match_score = (len(matched_skills) / len(job_skills_set)) * 100 if job_skills_set else 0

    # Calculate overall ATS score
    ats_score = round((similarity_score * 0.7) + (skill_match_score * 0.3), 2)
    return ats_score, list(job_skills_set - matched_skills)  # Convert missing_skills back to list

# Recommend jobs based on ATS score
def recommend_jobs(resume_text, resume_skills):
    """Fetches job descriptions and recommends the best jobs."""
    jobs = fetch_jobs()
    job_scores = []

    for title, description, skills in jobs:
        job_skills = set(skills.lower().split(", "))  # Convert stored skills into a set
        ats_score, missing_skills = calculate_ats_score(resume_text, description, resume_skills, job_skills)
        job_scores.append({
            "title": title,
            "ats_score": ats_score,
            "missing_skills": missing_skills,
            "description": description,  # Include description if needed
            "skills": job_skills  # Include job_skills if needed
        })

    job_scores.sort(key=lambda x: x['ats_score'], reverse=True)  # Sort by ATS score (highest first)
    
    if not job_scores:
        return [{"title": "No suitable jobs found", "ats_score": 0, "missing_skills": [], "description": "", "skills": set()}]  # Handle empty recommendations

    return job_scores[:3]  # Return top 3 job recommendations
# Return top 3 job recommendations


# Extract text from uploaded PDF
import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_input):
    text = ""
    try:
        if isinstance(pdf_input, BytesIO):
            pdf_input.seek(0)  # Reset the stream position to the beginning
            reader = PyPDF2.PdfReader(pdf_input)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += " " + page_text
        else:
            raise ValueError("Invalid input type. Expected BytesIO.")
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
    
    return text.strip()# Remove leading/trailing spaces # Remove leading/trailing spaces


@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_from_directory(app.config['GENERATED_UPLOAD_FOLDER'], filename, as_attachment=True, mimetype='application/pdf')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if 'user_name' not in session or session.get('user_role') != 'user':
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']
    file = request.files.get('resume')
    
    if not file or file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF allowed."}), 400

    # Read the file content first
    file_content = file.read()
    
    # Check if file is empty
    if not file_content:
        return jsonify({"error": "Uploaded file is empty"}), 400
    
    # Save to GridFS
    file.seek(0)  # Reset pointer before saving
    file_id = fs.put(file, filename=file.filename, content_type="application/pdf")

    # Read again for text extraction
    file_stream = BytesIO(file_content)
    resume_text = extract_text_from_pdf(file_stream)
    
    resume_skills = list(extract_skills(resume_text)) if resume_text else []
    
    job_recommendations = recommend_jobs(resume_text, resume_skills) if resume_text else []
    ats_score, missing_skills = ("N/A", [])
    
    if job_recommendations:
        ats_score, missing_skills = calculate_ats_score(
            resume_text, job_recommendations[0]['description'], resume_skills, job_recommendations[0]['skills']
        )
        missing_skills = list(missing_skills)
    
    for job in job_recommendations:
        job['skills'] = list(job.get('skills', []))  # Convert skills to list
        job['missing_skills'] = list(job.get('missing_skills', [])) 
    
    # Prepare user resume data
    user_resume_data = {
        "resume_pdf_id": file_id,  # Save the GridFS file ID
        "upload_text": resume_text,
        "extracted_skills": resume_skills,
        "ats_score": ats_score,
        "missing_skills": missing_skills,
        "job_recommendations": job_recommendations,
        "upload_date": datetime.datetime.utcnow()
    }
     
    
    try:
        # Update the user's document in the database
        collection.update_one({"user_name": user_name}, {"$set": user_resume_data}, upsert=True)
        
        return jsonify({
            "message": "Resume uploaded successfully!",
            "resume_text": resume_text,
            "ats_score": ats_score,
            "missing_skills": missing_skills,
            "job_recommendations": job_recommendations,
            "download_url":url_for('download_resume', pdf_id=str(file_id), _external=True),
            "profile_url": url_for('view_profile', _external=True)
        })
    except Exception as e:
        print(f"MongoDB Error: {e}")
        return jsonify({"error": "An error occurred while saving the resume."}), 500
import time
def upload_to_cloudinary(image_data, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = cloudinary.uploader.upload(image_data, resource_type="image")
            return response
        except CloudinaryError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                raise  # Re-raise the exception after all retries fail
@app.route("/submit", methods=["POST"])
def submit():
    if 'user_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']
    data = request.json

    try:
        # Decode image data
        image_data = base64.b64decode(data['photo'].split(",")[1])
        print("Image data length:", len(image_data))  # Debug: Check the size of the image data

        # Upload photo to Cloudinary
        try:
            photo_response = upload_to_cloudinary(image_data)
            photo_url = photo_response['secure_url']
        except CloudinaryError as e:
            return jsonify({"error": f"Failed to upload photo to Cloudinary: {e}"}), 500

        # Generate PDF
        pdf_filename = f"resume_{data['name']}.pdf"
        pdf_path = os.path.join(app.config['GENERATED_UPLOAD_FOLDER'], pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"Name: {data['name']}", styles['Title']),
            Spacer(1, 0.2 * inch),
            Paragraph(f"Email: {data['email']}", styles['BodyText']),
            Paragraph(f"Phone: {data['phone']}", styles['BodyText']),
            Paragraph(f"Skills: {', '.join(data['skills'])}", styles['BodyText']),
            Paragraph(f"Summary: {data['summary']}", styles['BodyText']),
            Paragraph("Experience:", styles['Heading2']),
            Paragraph(data['experience'], styles['BodyText']),
            Paragraph("Education:", styles['Heading2']),
            Paragraph(data['education'], styles['BodyText'])
        ]
        doc.build(story)

        # Upload PDF to Cloudinary
        with open(pdf_path, "rb") as pdf_file:
            pdf_response = cloudinary.uploader.upload(pdf_file, resource_type="raw")
            pdf_url = pdf_response['secure_url']

        # Extract text from PDF
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes_io = BytesIO(pdf_file.read())  # Convert file to BytesIO
        resume_text = extract_text_from_pdf(pdf_bytes_io)
        resume_skills = list(data['skills']) if 'skills' in data else []
        job_recommendations = recommend_jobs(resume_text, resume_skills) if resume_text else []
        ats_score, missing_skills = ("N/A", [])

        if job_recommendations:
            ats_score, missing_skills = calculate_ats_score(
                resume_text, job_recommendations[0]['description'], resume_skills, job_recommendations[0]['skills']
            )
            missing_skills = list(missing_skills)
        for job in job_recommendations:
           job['skills'] = list(job.get('skills', []))  # Convert skills to list
           job['missing_skills'] = list(job.get('missing_skills', []))

        # Prepare user data
        user_data = {
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "skills": list(resume_skills),
            "summary": data['summary'],
            "experience": data['experience'],
            "education": data['education'],
            "resume_url": pdf_url,
            "photo_url": photo_url,
            "resume_text": resume_text,
            "ats_score": ats_score,
            "missing_skills": list(missing_skills),
            "generated_job_recommendations": job_recommendations,
            "upload_date": datetime.datetime.utcnow()
        }

        # Update user data in MongoDB
        try:
            collection.update_one({"name": user_name}, {"$set": user_data}, upsert=True)
            return jsonify({
                "message": "Resume generated successfully!",
                "resume_text": resume_text,
                "ats_score": ats_score,
                "missing_skills": missing_skills,
                "job_recommendations": job_recommendations,
                "download_url": pdf_url,
                "profile_url": url_for('view_profile', _external=True)
            })
        except Exception as e:
            print(f"MongoDB Error: {e}")
            return jsonify({"error": "An error occurred while saving the resume."}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
@app.route('/download_resume/<pdf_id>')
def download_resume(pdf_id):
    """Serves the resume file from GridFS."""
    try:
        file = fs.get(ObjectId(pdf_id))
        if not file:
            return jsonify({"error": "File not found in GridFS"}), 404
        
        return send_file(
            BytesIO(file.read()),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=file.filename
        )
    except Exception as e:
        print(f"Error serving file: {e}")
        return jsonify({"error": "File not found"}), 404

@app.route('/view_resume/<user_id>')  # Example route
def view_resume(user_id):
    user = collection.find_one({"_id": ObjectId(user_id)})
    return render_template('view_resume.html', user=user)
@app.route('/view_resume_upload/<resume_pdf_id>')  # Example route
def view_resume_upload(resume_pdf_id):
    user = collection.find_one({"resume_pdf_id": ObjectId(resume_pdf_id)})
    return render_template('view_resume.html', user=user)
@app.route('/resume_delete', methods=['POST'])
def resume_delete():
    if 'user_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']
    user = collection.find_one({"user_name": user_name})

    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # 1. Delete from GridFS
        if user.get('resume_pdf_id'):  # Check if a resume exists
            fs.delete(ObjectId(user['resume_pdf_id']))

        # 2. Update user record in MongoDB
        collection.update_one(
            {"name": user_name},
            {"$unset": {"resume_pdf_id": "", "extracted_skills": "", "ats_score": "", "missing_skills": "", "job_recommendations": ""}} # Clear all resume related information
        )

        return redirect(url_for('success'))  # Redirect back to the success page

    except Exception as e:
        print(f"Error deleting resume: {e}")
        return jsonify({"error": "An error occurred while deleting the resume."}), 500
@app.route('/view_profile')
def view_profile():
    # Check if the session is for a user
    if 'user_name' not in session or session.get('user_role') != 'user':
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']
    user = collection.find_one({"user_name": user_name})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return render_template('success.html', user=user)
@app.route('/admin_view_profile/<user_id>')
def admin_view_profile(user_id):
    # Check if the session is for a user
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return jsonify({"error": "User not logged in"}), 401

    
    user = collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return render_template('success.html', user=user)


@app.route("/update_resume", methods=["GET", "POST"])
def update_resume():
    if 'user_name' not in session:
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']

    if request.method == "GET":
        user = collection.find_one({"user_name": user_name})
        if not user:
            return jsonify({"error": "User not found"}), 404
        return render_template("update_resume.html", user=user)

    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Upload photo to Cloudinary
        image_data = base64.b64decode(data['photo'].split(",")[1])
        photo_response = cloudinary.uploader.upload(image_data, resource_type="image")
        photo_url = photo_response['secure_url']

        # Generate PDF
        pdf_filename = f"resume_{data['name']}.pdf"
        pdf_path = os.path.join(app.config['UPDATE_UPLOAD_FOLDER'], pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"Name: {data['name']}", styles['Title']),
            Spacer(1, 0.2 * inch),
            Paragraph(f"Email: {data['email']}", styles['BodyText']),
            Paragraph(f"Phone: {data['phone']}", styles['BodyText']),
            Paragraph(f"Skills: {', '.join(data['skills'])}", styles['BodyText']),
            Paragraph(f"Summary: {data['summary']}", styles['BodyText']),
            Paragraph("Experience:", styles['Heading2']),
            Paragraph(data['experience'], styles['BodyText']),
            Paragraph("Education:", styles['Heading2']),
            Paragraph(data['education'], styles['BodyText'])
        ]
        doc.build(story)

        # Upload PDF to Cloudinary
        pdf_response = cloudinary.uploader.upload(pdf_path, resource_type="raw")
        pdf_url = pdf_response['secure_url']
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes_io = BytesIO(pdf_file.read())  
        resume_text = extract_text_from_pdf(pdf_bytes_io)
        resume_skills = data.get('skills', [])
        job_recommendations = recommend_jobs(resume_text, resume_skills) if resume_text else []

        ats_score, missing_skills = ("N/A", [])
        if job_recommendations:
            ats_score, missing_skills = calculate_ats_score(
                resume_text, job_recommendations[0]["description"], resume_skills, job_recommendations[0]["skills"]
            )
            missing_skills = list(missing_skills)
        for job in job_recommendations:
           job['skills'] = list(job.get('skills', []))  # Convert skills to list
           job['missing_skills'] = list(job.get('missing_skills', []))

        updated_resume_data = {
            "resume_url": pdf_url,  # Use Cloudinary URL
            "resume_text": resume_text,
            "extracted_skills": list(resume_skills),
            "ats_score": ats_score,
            "missing_skills": list(missing_skills),
            "job_recommendations": job_recommendations,
            "upload_date": datetime.datetime.utcnow(),
            "photo_url": photo_url,
            "name": data.get('name'),
            "email": data.get('email'),
            "phone": data.get('phone'),
            "summary": data.get('summary'),
            "experience": data.get('experience'),
            "education": data.get('education')
        }

        try:
            collection.update_one({"name": user_name}, {"$set": updated_resume_data})
            return jsonify({
                "message": "Resume updated successfully!",
                "resume_text": resume_text,
                "ats_score": ats_score,
                "missing_skills": missing_skills,
                "job_recommendations": job_recommendations,
                "download_url": pdf_url,  # Use Cloudinary URL
                "profile_url": url_for("view_profile", _external=True),
            })
        except Exception as e:
            print(f"MongoDB Error: {e}")
            return jsonify({"error": "An error occurred while updating the resume."}), 500

@app.route("/get_admin_update_resume/<user_id>", methods=["GET"])
def get_admin_update_resume(user_id):
          # Get user_id from query parameters
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        user = collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404

        return render_template("admin_update_resume.html", user=user)
@app.route("/admin_update_resume/<user_id>", methods=["POST"])
def admin_update_resume(user_id):
    if 'admin_name' not in session:
        return jsonify({"error": "Admin not logged in"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Upload photo to Cloudinary
    image_data = base64.b64decode(data['photo'].split(",")[1])
    photo_response = cloudinary.uploader.upload(image_data, resource_type="image")
    photo_url = photo_response['secure_url']

    # Generate PDF
    pdf_filename = f"resume_{data['name']}.pdf"
    pdf_path = os.path.join(app.config['UPDATE_UPLOAD_FOLDER'], pdf_filename)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Name: {data['name']}", styles['Title']),
        Spacer(1, 0.2 * inch),
        Paragraph(f"Email: {data['email']}", styles['BodyText']),
        Paragraph(f"Phone: {data['phone']}", styles['BodyText']),
        Paragraph(f"Skills: {', '.join(data['skills'])}", styles['BodyText']),
        Paragraph(f"Summary: {data['summary']}", styles['BodyText']),
        Paragraph("Experience:", styles['Heading2']),
        Paragraph(data['experience'], styles['BodyText']),
        Paragraph("Education:", styles['Heading2']),
        Paragraph(data['education'], styles['BodyText'])
    ]
    doc.build(story)

    # Upload PDF to Cloudinary
    pdf_response = cloudinary.uploader.upload(pdf_path, resource_type="raw")
    pdf_url = pdf_response['secure_url']
    with open(pdf_path, "rb") as pdf_file:
            pdf_bytes_io = BytesIO(pdf_file.read())
    resume_text = extract_text_from_pdf(pdf_bytes_io)
    resume_skills = data.get('skills', [])
    job_recommendations = recommend_jobs(resume_text, resume_skills) if resume_text else []

    ats_score, missing_skills = ("N/A", [])
    if job_recommendations:
        ats_score, missing_skills = calculate_ats_score(
            resume_text, job_recommendations[0]["description"], resume_skills, job_recommendations[0]["skills"]
        )
        missing_skills = list(missing_skills)
    for job in job_recommendations:
           job['skills'] = list(job.get('skills', []))  # Convert skills to list
           job['missing_skills'] = list(job.get('missing_skills', []))

    updated_resume_data = {
        "resume_url": pdf_url,  # Use Cloudinary URL
        "resume_text": resume_text,
        "extracted_skills": list(resume_skills),
        "ats_score": ats_score,
        "missing_skills": list(missing_skills),
        "job_recommendations": job_recommendations,
        "upload_date": datetime.datetime.utcnow(),
        "photo_url": photo_url,
        "name": data.get('name'),
        "email": data.get('email'),
        "phone": data.get('phone'),
        "summary": data.get('summary'),
        "experience": data.get('experience'),
        "education": data.get('education')
    }

    try:
        collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_resume_data})
        return jsonify({
            "message": "Resume updated successfully!",
            "resume_text": resume_text,
            "ats_score": ats_score,
            "missing_skills": missing_skills,
            "job_recommendations": job_recommendations,
            "download_url": pdf_url,  # Use Cloudinary URL
            "profile_url": url_for("admin_view_profile", user_id=user_id, _external=True),
        })
    except Exception as e:
        print(f"MongoDB Error: {e}")
        return jsonify({"error": "An error occurred while updating the resume."}), 500
@app.route('/download_resume/<pdf_url>')
def generate_download_resume(pdf_url):
    """Serves the resume file from Cloudinary."""
    try:
        # Fetch the file from Cloudinary
        response = cloudinary.api.resource(pdf_url, resource_type="raw")
        if not response:
            return jsonify({"error": "File not found in Cloudinary"}), 404
        
        # Get the secure URL of the file
        file_url = response['secure_url']
        
        # Redirect to the file URL for download
        return redirect(file_url)
    
    except CloudinaryError as e:
        print(f"Cloudinary Error: {e}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500
@app.route('/download_photo/<photo_url>')
def download_photo(photo_url):
    """Serves the photo file from Cloudinary."""
    try:
        # Fetch the file from Cloudinary
        response = cloudinary.api.resource(photo_url, resource_type="image")
        if not response:
            return jsonify({"error": "File not found in Cloudinary"}), 404
        
        # Get the secure URL of the file
        file_url = response['secure_url']
        
        # Redirect to the file URL for download
        return redirect(file_url)
    
    except CloudinaryError as e:
        print(f"Cloudinary Error: {e}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

from urllib.parse import unquote
@app.route("/apply_job_user", methods=["GET"])
def apply_job_user():
    jobs=get_jobs_from_db()
    return render_template("apply.html",jobs=jobs)
@app.route("/apply_job/<job_title>", methods=["POST"])
def apply_job(job_title):
    # Decode the job_title to handle spaces and special characters
    job_title = unquote(job_title)
    print(f"Job title received: {job_title}")

    if 'user_name' not in session or session.get('user_role') != 'user':
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']
    user = collection.find_one({"user_name": user_name})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch the job details from the database using job_title
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, skills FROM job_descriptions WHERE title = ?", (job_title,))
    job = cursor.fetchone()
    conn.close()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    job_title, job_description, job_skills = job

    # Check if the user has already applied for this job
    existing_application = job_applications_collection.find_one({
        "user_name": user_name,
        "job_title": job_title
    })

    if existing_application:
        return jsonify({"error": "You have already applied for this job"}), 400

    # Use the user's existing resume or generate a new one
    if user.get('resume_pdf_id'):
        resume_pdf_id = user['resume_pdf_id']
        resume_text = user.get('upload_text', '')
    else:
        return jsonify({"error": "No resume found. Please upload resume first."}), 400

    # Extract skills from the resume

    # Save the job application
    application_data = {
        "user_name": user_name,
        "job_title": job_title,
        "resume_pdf_id": resume_pdf_id,
        "resume_text": resume_text,
        "ats_score": user["ats_score"],
        "missing_skills": user["missing_skills"],
        "status": "pending",  # Initial status
        "application_date": datetime.datetime.utcnow()
    }

    job_applications_collection.insert_one(application_data)
    collection.update_one(
            {"user_name": user_name},
            {"$set": {"application_status": list(application_data)}}
        )

    return jsonify({
        "message": "Job application submitted successfully!",
        "ats_score": user["ats_score"],
        "missing_skills":user["missing_skills"],
        "status": "pending"
    })
@app.route("/view_applications", methods=["GET"])
def view_applications():
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return jsonify({"error": "Admin not logged in"}), 401

    # Fetch all job applications
    applications = list(job_applications_collection.find({}))

    return render_template("view_applications.html", applications=applications)
@app.route("/update_application_status/<application_id>", methods=["POST"])
def update_application_status(application_id):
    # Check if the admin is logged in
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return jsonify({"error": "Admin not logged in"}), 401

    # Validate the request data
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Status is required"}), 400

    status = data['status']
    if status not in ["accepted", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    try:
        # Fetch the application to get the user_name
        application = job_applications_collection.find_one({"_id": ObjectId(application_id)})
        if not application:
            return jsonify({"error": "Application not found"}), 404

        user_name = application.get("user_name")
        if not user_name:
            return jsonify({"error": "User not found in application"}), 404

        # Update the application status in job_applications_collection
        job_applications_collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": {"status": status}}
        )

        # Update the user's document in the collection (users database)
        collection.update_one(
            {"user_name": user_name},
            {"$set": {"application_status": application}}
        )

        return jsonify({"message": f"Application status changed to {status}"})

    except Exception as e:
        print(f"Error updating application status: {e}")
        return jsonify({"error": "An error occurred while updating the application status"}), 500

@app.route("/delete_application/<application_id>", methods=["DELETE"])
def user_delete_application(application_id):
    # Check if the user is logged in
    if 'user_name' not in session or session.get('user_role') != 'user':
        return jsonify({"error": "User not logged in"}), 401

    user_name = session['user_name']

    # Find the application by its ID and ensure it belongs to the logged-in user
    application = collection.find_one({
        "_id": ObjectId(application_id),
        "user_name": user_name
    })
    if not application:
        return jsonify({"error": "Application not found or unauthorized"}), 404

    # Delete the application
    collection.update({ "user_name":user_name }, { "$unset": { "application_status": "" } })

    return jsonify({"message": "Application deleted successfully!"})
@app.route("/view_job/<job_title>", methods=["GET"])
def view_job(job_title):
    job_title = unquote(job_title)
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions WHERE title = ?", (job_title,))
    jobs = cursor.fetchone()
    print(jobs)
    return render_template("view_job.html",jobs=jobs)


def update_job(job_id, title, description, skills, experience, projects, education, qualifications):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE job_descriptions
        SET title = ?, description = ?, skills = ?, experience = ?, projects = ?, education = ?, qualifications = ?
        WHERE id = ?
    """, (title, description, skills, experience, projects, education, qualifications, job_id))
    conn.commit()
    conn.close()

def insert_job(title, description, skills, experience, projects, education, qualifications):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    # Insert the new job into the database
    cursor.execute("""
        INSERT INTO job_descriptions (title, description, skills, experience, projects, education, qualifications)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, skills, experience, projects, education, qualifications))

    conn.commit()  
    conn.close()   
@app.route("/admin_jobs", methods=["GET", "POST"])
def admin_jobs():
    if 'admin_name' not in session or session.get('admin_role') != 'admin':
        return jsonify({"error": "Admin not logged in"}), 401
    if request.method == "POST":
        # Handle job insertion or update
        title = request.form.get("title")
        description = request.form.get("description")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        projects = request.form.get("projects")
        education = request.form.get("education")
        qualifications = request.form.get("qualifications")
        job_id = request.form.get("job_id")

        if job_id:  # Update existing job
            update_job(job_id, title, description, skills, experience, projects, education, qualifications)
            flash("Job updated successfully!", "success")
        else:  # Insert new job
            insert_job(title, description, skills, experience, projects, education, qualifications)
            flash("Job added successfully!", "success")

        return redirect(url_for("admin_jobs"))

    # Fetch all jobs for display
    jobs = fetch_admin_jobs()
    return render_template("admin_jobs.html", jobs=jobs)
@app.route("/admin/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_descriptions WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()
    flash("Job deleted successfully!", "success")
    return redirect(url_for("admin_jobs"))
@app.route("/admin/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = fetch_job_by_id(job_id)
    if job:
        return jsonify({
            "id": job[0],
            "title": job[1],
            "description": job[2],
            "skills": job[3],
            "experience": job[4],
            "projects": job[5],
            "education": job[6],
            "qualifications": job[7]
        })
    return jsonify({"error": "Job not found"}), 404
def fetch_job_by_id(job_id):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_descriptions WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job
if __name__ == "__main__":
    app.run(debug=os.getenv('DEBUG', 'False') == 'True')

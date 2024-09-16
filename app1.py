from datetime import date
from flask import Flask, jsonify, request, render_template
import face_recognition
from PIL import Image
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from io import BytesIO

app = Flask(__name__)
registered_data = {}

# Configure Cloudinary
cloudinary.config(
    cloud_name='dpdqhtova',
    api_key='419217971722169',
    api_secret='ak01Sgbsa4CqxUWW97r2SLrI6Ec'
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route("/register", methods=['POST'])
def register():
    name = request.form.get("name")
    photo = request.files['photo']
    upload_result = cloudinary.uploader.upload(photo)
    registered_data[name] = upload_result['url']
    response = {"success": True, 'name': name}
    return jsonify(response)

@app.route("/login", methods=["POST", "GET"])
def login():
    name = request.form.get("name")
    photo = request.files['photo']
    upload_result = cloudinary.uploader.upload(photo)
    login_image_url = upload_result['url']
    print(login_image_url)
    response = requests.get(login_image_url)
    img = Image.open(BytesIO(response.content))
    local_image_path = 'local_image.png'
    img.save(local_image_path)

    login_image = face_recognition.load_image_file(local_image_path)
    login_face_encodings = face_recognition.face_encodings(login_image)
    for registered_name, image_url in registered_data.items():
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        local_image_path = 'local_image.png'
        img.save(local_image_path)
        registered_image = face_recognition.load_image_file(local_image_path)
        registered_face_encodings = face_recognition.face_encodings(registered_image)
        if len(registered_face_encodings) > 0 and len(login_face_encodings) > 0:
            matches = face_recognition.compare_faces(registered_face_encodings, login_face_encodings[0])
            if any(matches):
                response = {"success": True, "name": registered_name, 'image_url': image_url}
                print(response['image_url'])
                return jsonify(response)
    response = {"success": False}
    return jsonify(response)

@app.route("/success", methods=['GET'])
def success():
    user_name = request.args.get("user_name")
    print(user_name)
    image_url = request.args.get("image_url")
    print(image_url)
    return render_template("success.html", user_name=user_name, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=False)

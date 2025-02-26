let video;
let canvas;
let nameInput;
let rollnoInput;
let branchInput;
let registrationnoInput;
let bioInput;
let password;
function init() {
    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    nameInput = document.getElementById("name");
    rollnoInput = document.getElementById("rollno");
    branchInput = document.getElementById("branch");
    registrationnoInput = document.getElementById("registrationno");
    bioInput = document.getElementById("bio");
    password=document.getElementById("password")
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
                video.play();
            })
            .catch(function(error) {
                console.error("Error accessing the camera: ", error);
            });
    } else {
        console.error("getUserMedia not supported in this browser.");
    }
}

function capture() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.style.display = "block";
    video.style.display = "none";
}

function register() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const name = nameInput.value;
    const rollno = rollnoInput.value;
    const branch = branchInput.value;
    const registrationno = registrationnoInput.value;
    const bio = bioInput.value;
    const photo = dataURITOBlob(canvas.toDataURL());

    if (!name || !rollno || !branch || !registrationno || !bio || !photo) {
        alert("All fields are required, please.");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("rollno", rollno);
    formData.append("branch", branch);
    formData.append("registrationno", registrationno);
    formData.append("bio", bio);
    formData.append("photo", photo, `${name}.jpg`);

    fetch("/register", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Data successfully registered");
            window.location.href = "/user_login";
        } else {
            alert("Sorry, registration not successful");
        }
    })
    .catch(error => {
        alert(error);
        console.log("Error", error);
    });
}


function admin_register() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const name = nameInput.value;
    const photo = dataURITOBlob(canvas.toDataURL());
    const password=document.getElementById('password').value;
    if (!name  || !photo  || !password) {
        alert("All fields are required, please.");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("password", password);
    formData.append("photo", photo, `${name}.jpg`);

    fetch("/admin_register", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Data successfully registered");
            window.location.href = "/admin_login";
        } else {
            alert("Sorry, registration not successful");
        }
    })
    .catch(error => {
        console.log("Error", error);
    });
}

function login() {
    const user_name = nameInput.value;
    const password = passwordInput.value;

    if (!name || !password) {
        alert("Name and password are required, please.");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("password", password);

    fetch("/login", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Login successful");
            window.location.href = `/success?user_name=${encodeURIComponent(data.user_name)}`;
        } else {
            alert("Login failed: " + data.error);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred during login.");
    });
}


function admin_login() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const name = nameInput.value;
    const photo = dataURITOBlob(canvas.toDataURL());
    const password = document.getElementById('password').value;
    if (!name || !photo|| !password) {
        alert("Name and photo required, please.");
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("photo", photo, `${name}.jpg`);
    formData.append("password",password)
    fetch("/admin_login", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Login successful");
            window.location.href = "/admin";
        } else {
            alert("Login not successful");
        }
    })
    .catch(error => {
        console.log("Error", error);
    });
}
function dataURITOBlob(dataURI) {
    var byteString;
    if (dataURI.split(',')[0].indexOf('base64') >= 0)
        byteString = atob(dataURI.split(',')[1]);
    else
        byteString = unescape(dataURI.split(',')[1]);

    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    var ia = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ia], { type: mimeString });
}
function register1() {
    const name = document.getElementById('name').value;
    const rollno = document.getElementById('rollno').value;
    const registrationno = document.getElementById('registrationno').value;
    const email = document.getElementById('email').value;
    const branch = document.getElementById('branch').value;
    const degree = document.getElementById('degree').value;
    const skills = Array.from(document.getElementById('skills').selectedOptions).map(option => option.value);
    const experience = document.getElementById('experience').value;
    const bio = document.getElementById('bio').value;
    const hobbies = document.getElementById('hobbies').value;

    // Store data in localStorage
    localStorage.setItem('name', name);
    localStorage.setItem('rollno', rollno);
    localStorage.setItem('registrationno', registrationno);
    localStorage.setItem('email', email);
    localStorage.setItem('branch', branch);
    localStorage.setItem('degree', degree);
    localStorage.setItem('skills', JSON.stringify(skills));
    localStorage.setItem('experience', experience);
    localStorage.setItem('bio', bio);
    localStorage.setItem('hobbies', hobbies);

    // Redirect to display.html
    window.location.href = 'display.html';
}

// Display data on display.html
if (window.location.pathname.endsWith('display.html')) {
    document.getElementById('displayName').textContent = localStorage.getItem('name');
    document.getElementById('displayRollNo').textContent = localStorage.getItem('rollno');
    document.getElementById('displayRegistrationNo').textContent = localStorage.getItem('registrationno');
    document.getElementById('displayEmail').textContent = localStorage.getItem('email');
    document.getElementById('displayBranch').textContent = localStorage.getItem('branch');
    document.getElementById('displayDegree').textContent = localStorage.getItem('degree');
    
    const skills = JSON.parse(localStorage.getItem('skills'));
    const skillsList = document.getElementById('displaySkills');
    skills.forEach(skill => {
        const li = document.createElement('li');
        li.textContent = skill;
        skillsList.appendChild(li);
    });

    document.getElementById('displayExperience').textContent = localStorage.getItem('experience');
    document.getElementById('displayBio').textContent = localStorage.getItem('bio');
    document.getElementById('displayHobbies').textContent = localStorage.getItem('hobbies');
}
init();

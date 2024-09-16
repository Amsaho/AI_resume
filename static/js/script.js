let video;
let canvas;
let nameInput;

function init() {
    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    nameInput = document.getElementById("name");
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Request access to the camera
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                // Set the video source to the stream
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
    const photo = dataURITOBlob(canvas.toDataURL());
    if (!name || !photo) {
        alert("Name and photo required, please.");
        return;
    }
    const formData = new FormData();
    formData.append("name", name);
    formData.append("photo", photo, `${name}.jpg`);
    fetch("/register", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Data successfully registered");
            window.location.href = "/login";
        } else {
            alert("Sorry, registration not successful");
        }
    })
    .catch(error => {
        console.log("Error", error);
    });
}

function login() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const name = nameInput.value;
    const photo = dataURITOBlob(canvas.toDataURL());
    if (!name || !photo) {
        alert("Name required, please.");
        return;
    }
    const formData = new FormData();
    formData.append("name", name);
    formData.append("photo", photo, `${name}.jpg`);
    fetch("/login", {
        method: "POST",
        body: formData
    }).then(response => response.json()).then(data => {
        console.log(data);
        if (data.success) {
            alert("Login successful");
            window.location.href = `/success?user_name=${encodeURIComponent(data.name)}&image_url=${encodeURIComponent(data.image_url)}`;
        } else {
            alert("Login not successful");
        }
    }).catch(error => {
        console.log("Error", error);
    });
}

function dataURITOBlob(dataURI) {
    // Convert base64/URLEncoded data component to raw binary data held in a string
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

init();

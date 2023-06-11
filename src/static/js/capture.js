const personImageHolder = document.getElementById('nguyen-person-image');
const captureButton = document.getElementById('nguyen-person-image-camera');
const camera = document.getElementById('nguyen-person-camera');
const cameraCanvas = document.getElementById('nguyen-person-camera-canvas');

let streaming = false;


function capture() {
    if (!streaming) {
        startCapture();
    } else {
        takePhoto();
        stopCapture();
    }
}

function startCapture() {

    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

    navigator.mediaDevices.getUserMedia({video: true, audio: false})
        .then((stream) => {
            captureButton.innerText = "Take photo";
            camera.srcObject = stream;
            camera.play();
        })
        .catch((err) => {
            console.log("An error occurred: " + err);
        });

    camera.addEventListener('canplay', (ev) => {
        if (!streaming) {
            let width = 300;
            let = height = camera.videoHeight / (camera.videoWidth / width);
            camera.style.display = "block";
            camera.setAttribute('width', width);
            camera.setAttribute('height', height);
            streaming = true;
        }
    }, false);
}


function takePhoto() {
    if (streaming) {
        let context = cameraCanvas.getContext('2d');
        cameraCanvas.width = camera.width;
        cameraCanvas.height = camera.height;
        context.drawImage(camera, 0, 0, cameraCanvas.width, cameraCanvas.height);

        let data = cameraCanvas.toDataURL('image/png');
        personImageHolder.setAttribute('src', data);

        cameraCanvas.toBlob(blob => {
            const file = new File([blob], "capture.png", {
                type: 'image/png',
                lastModified: new Date(),
            });
            const input = document.getElementById('nguyen-person-image-uploader');
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
          });
    }
}

// Stop capture
function stopCapture() {
    captureButton.innerText = "Capture camera";
    if (streaming) {
        const stream = camera.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach(function (track) {
            track.stop();
        });
        streaming = false;
        camera.srcObject = null;
        camera.style.display = "none";
    }
}
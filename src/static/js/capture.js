const personImageHolder = document.getElementById('nguyen-person-image');
const captureButton = document.getElementById('nguyen-person-image-camera');
const camera = document.getElementById('nguyen-person-camera');
const cameraCanvas = document.getElementById('nguyen-person-camera-canvas');

let streaming = false;


function capture() {
    if (!streaming) {
        queryCamera();
    } else {
        takePhoto();
        stopCapture();
    }
}

function queryCamera() {
    navigator.mediaDevices.enumerateDevices()
        .then(function (videoDevices) {
    
        // Check if there are multiple cameras available
        console.error(videoDevices.length);
        if (videoDevices.length > 0) {
            startCapture(videoDevices[videoDevices.length - 1].deviceId);
        } else {
            // No cameras available
            console.error('No cameras found.');
        }
        })
        .catch(function (error) {
        console.error('Error enumerating devices:', error);
        });
}

function startCapture(deviceId) {
    const constraints = { video: { deviceId: deviceId  } };

    navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
            captureButton.innerText = "Take photo";
            camera.srcObject = stream;
            camera.play();

            // Get the video track from the stream
            var videoTrack = stream.getVideoTracks()[0];

            // Check if the 'applyConstraints' method is available
            if ('applyConstraints' in videoTrack) {
            // Define the brightness constraint
            var constraints = { advanced: [{ brightness: 0 }] };

            // Apply the brightness constraint to the video track
            videoTrack.applyConstraints(constraints)
                .catch(function (error) {
                console.error('Error applying constraints:', error);
                });
            } else {
            console.warn('Brightness adjustment not supported.');
            }
        })
        .catch((err) => {
            console.log("An error occurred: " + err);
        });

    camera.addEventListener('canplay', (ev) => {
        if (!streaming) {
            let width = 300;
            let = height = camera.videoHeight / (camera.videoWidth / width);
            personImageHolder.style.display = "none"
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
        personImageHolder.style.display = "block"
    }
}
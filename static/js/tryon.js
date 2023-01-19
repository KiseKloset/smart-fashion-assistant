const personImageInput = document.getElementById('nguyen-person-image-uploader');
const clothImageInput = document.getElementById('nguyen-cloth-image-uploader');
const resultImage = document.getElementById('nguyen-result-image');

function uploadReferenceImage(id) {
    const imageInput = document.getElementById(id);
    imageInput.click();
}

function uploadReferenceImageInternal(element, imgID) {
    const refImage = document.getElementById(imgID);
    const file = element.files[0];
    const imageType = /image.*/;

    if (file.type.match(imageType)) {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => {
            refImage.src = reader.result;
        }
    } else {
        window.alert('Invalid image file.');
    }
}

function tryOn() {
    if (personImageInput.files.length < 1) {
        window.alert("Upload person image first");
        return;
    }
    if (clothImageInput.files.length < 1) {
        window.alert("Upload cloth image first");
        return;
    }

    const body = new FormData();
    body.append("person_image", personImageInput.files[0]);
    body.append("cloth_image", clothImageInput.files[0]);

    fetch('/try-on/try-on', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
        body: body
    }).then(async (response) => {
        let data = await response.json()
        if (data["message"] == "success") {
            resultImage.src = data["result"];
        }
        else {
            window.alert("Something wrong. Please check your input and try again next time");
        }
    })
}
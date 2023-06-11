const personImageInput = document.getElementById('nguyen-person-image-uploader');
const garmentImageInput = document.getElementById('nguyen-garment-image-uploader');
const resultImage = document.getElementById('nguyen-result-image');

function uploadReferenceImage(id) {
    const imageInput = document.getElementById(id);
    imageInput.files = (new DataTransfer()).files;
    imageInput.click();
}

function uploadReferenceImageInternal(element, imgID) {
    if (element.files.length < 1) return;

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
    if (garmentImageInput.files.length < 1) {
        window.alert("Upload garment image first");
        return;
    }

    const body = new FormData();
    body.append("person_image", personImageInput.files[0]);
    body.append("garment_image", garmentImageInput.files[0]);

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
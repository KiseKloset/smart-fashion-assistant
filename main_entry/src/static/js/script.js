const refImageInput = document.getElementById('tung-image-uploader');
const refImage = document.getElementById('tung-ref-image');
const resultImages = document.getElementById('tung-result-images');
const captionInput = document.getElementById('tung-caption-input');

let tryOnImages = {}

function uploadReferenceImage() {
    refImageInput.click();
}

function uploadReferenceImageInternal(element) {
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

function queryImages() {
    if (refImageInput.files.length < 1) {
        window.alert("Upload reference image first");
        return;
    }

    const body = new FormData();
    body.append("ref_image", refImageInput.files[0]);
    body.append("caption", captionInput.value);

    fetch('/tgir/retrieve', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
        body: body
    }).then(async (response) => {
        let data = await response.json()
        showImages(data)
    })
}

function showImages(data) {
    resultImages.replaceChildren();
    tryOnImages = {}

    for (category in data) {
        let categoryContainer = document.createElement("div");
        categoryContainer.classList.add("horizontal-layout");

        let label = createLabel(category)
        let resultImagesContainer = createResultImagesContainer(category, data[category]);

        categoryContainer.appendChild(label)
        categoryContainer.appendChild(resultImagesContainer)

        resultImages.appendChild(categoryContainer);
    }
}

function createLabel(labelName) {
    let label = document.createElement('span');
    label.innerText = labelName;
    return label;
}

function createResultImagesContainer(category, data) {
    let container = document.createElement("div");
    container.classList.add("horizontal-layout");
    container.classList.add("result-images");
    container.style.marginBottom = "20px";

    for (let i = 0; i < data.length; i++) {
        let image = document.createElement("img");
        image.style.maxHeight = "150px";
        image.src = data[i]["url"];
        image.id = data[i]["id"];
        image.onclick = function () { choose(category, this); }
        container.appendChild(image);
    }
    return container;
}

function choose(category, element) {
    tryOnImages[category] = element.id;

    let siblings = element.parentElement.children;
    for (let i = 0; i < siblings.length; i++) {
        siblings[i].style.border = "";
    }

    element.style.border = "3px solid #ff0000";
}
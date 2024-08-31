document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
    };
    reader.readAsDataURL(file);
});

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('image', document.getElementById('imageInput').files[0]);
    formData.append('size', document.getElementById('sizeInput').value);

    fetch('/compress', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'compressed_image.jpg';
        document.body.appendChild(a);
        a.click();
        a.remove();
        document.getElementById('result').textContent = 'Image compressed and downloaded successfully!';
    })
    .catch(error => {
        document.getElementById('result').textContent = 'Error: ' + error.message;
    });
});
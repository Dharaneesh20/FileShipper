document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadStatus = document.getElementById('uploadStatus');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    uploadForm.addEventListener('click', () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.click();

        input.onchange = async () => {
            for (let file of input.files) {
                await uploadFile(file);
            }
        };
    });

    // File drop handling
    uploadForm.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadForm.classList.add('bg-light');
    });

    uploadForm.addEventListener('dragleave', () => {
        uploadForm.classList.remove('bg-light');
    });

    uploadForm.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadForm.classList.remove('bg-light');
        
        const files = e.dataTransfer.files;
        for (let file of files) {
            await uploadFile(file);
        }
    });

    async function uploadFile(file) {
        uploadStatus.innerHTML = `<div class="alert alert-info">Uploading ${file.name}...</div>`;
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'same-origin'
            });
            
            let responseText;
            try {
                responseText = await response.text();
                const data = JSON.parse(responseText);
                
                if (response.ok) {
                    uploadStatus.innerHTML = `<div class="alert alert-success">${file.name} uploaded successfully!</div>`;
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    const errorMessage = data.error || 'Unknown error occurred';
                    uploadStatus.innerHTML = `<div class="alert alert-danger">Error uploading ${file.name}: ${errorMessage}</div>`;
                }
            } catch (parseError) {
                console.error('Error parsing response:', responseText);
                uploadStatus.innerHTML = `<div class="alert alert-danger">Error uploading ${file.name}: Server returned invalid response</div>`;
            }
        } catch (error) {
            uploadStatus.innerHTML = `<div class="alert alert-danger">Error uploading ${file.name}: ${error.message}</div>`;
            console.error('Upload error:', error);
        }
    }
});

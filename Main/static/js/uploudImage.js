document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const overlay = document.getElementById('overlay');
    const imageTableBody = document.querySelector('#image-table tbody');
    const popup = document.getElementById('popup');
    const popupMessage = document.getElementById('popup-message');

    dropArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (event) => handleFiles(event.target.files));

    window.addEventListener('dragenter', (event) => {
        event.preventDefault();
        overlay.classList.add('visible');
    });

    window.addEventListener('dragleave', (event) => {
        event.preventDefault();
        if (event.target === overlay || event.target === document.body) {
            overlay.classList.remove('visible');
        }
    });

    window.addEventListener('dragover', (event) => {
        event.preventDefault();
    });

    window.addEventListener('drop', (event) => {
        event.preventDefault();
        overlay.classList.remove('visible');
        const files = event.dataTransfer.files;
        handleFiles(files);
    });

    function handleFiles(files) {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('file', file);
        });

        fetch('', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                data.images.forEach(image => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><img src="${image.url}" alt="${image.name}" width="100"></td>
                        <td>${image.name}</td>
                        <td>${image.type}</td>
                    `;
                    imageTableBody.appendChild(tr);
                });
                popupMessage.textContent = data.message;
                popup.classList.add('visible');
            } else {
                popupMessage.textContent = data.message;
                popup.classList.add('visible');
            }
        })
        .catch(error => {
            popupMessage.textContent = 'Erro ao enviar a imagem.';
            popup.classList.add('visible');
            console.error('Fetch error:', error);
        });
    }
});
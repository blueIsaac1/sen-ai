document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const imageList = document.getElementById('image-list');
    const overlay = document.getElementById('overlay');
    const fileInput = document.getElementById('file-upload');

    // Previne o comportamento padrão
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Adiciona classes para o overlay
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        overlay.style.display = 'flex';
    }

    function unhighlight() {
        overlay.style.display = 'none';
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        [...files].forEach(addImageToTable);
    }

    function addImageToTable(file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = document.createElement('img');
            img.src = event.target.result;
            img.style.width = '50px'; // Ajuste o tamanho da imagem conforme necessário

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${img.outerHTML}</td>
                <td>${file.name}</td>
                <td>${file.type}</td>
            `;
            imageList.appendChild(row);
        };
        reader.readAsDataURL(file);
    }
});
const fileUpload = document.getElementById('file-upload');
const imageContainer = document.getElementById('imageContainer');
const uploadedImage = document.getElementById('uploadedImage');
const resetButton = document.getElementById('resetButton');
const uploadDiv = document.getElementById('drop-area');
const textoUploadBaixo = document.querySelector('.textoUploadBaixo');
const textoUploadCima = document.querySelector('.textoUploadCima');
const select_texto = document.querySelector('.select_texto');
const enviar_btn_upload = document.querySelector('.enviar_btn_upload');
const textoUploadForm = document.querySelector('.textoUploadForm');

// Evento para o upload da imagem
fileUpload.addEventListener('change', function() {
    const file = this.files[0]; // Pega o primeiro arquivo
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedImage.src = e.target.result; // Define a imagem
            imageContainer.style.display = 'flex'; // Mostra a div
            uploadDiv.style.display = 'none';
            textoUploadBaixo.style.display = 'none';
            textoUploadCima.style.display = 'none';
            resetButton.style.display = 'flex'
            select_texto.style.display = 'flex'
            enviar_btn_upload.style.display = 'flex'
            textoUploadForm.style.display = 'flex'
        }
        reader.readAsDataURL(file); // Lê o arquivo como URL
    }
});

// Evento para o botão de resetar
resetButton.addEventListener('click', function() {
    fileUpload.value = ''; // Limpa o input
    uploadedImage.src = ''; // Limpa a imagem
    textoUploadBaixo.style.display = 'flex';
    textoUploadCima.style.display = 'flex';
    uploadDiv.style.display = 'flex';
    imageContainer.style.display = 'none'; // Oculta a div
    resetButton.style.display = 'none'
    select_texto.style.display = 'none'
    enviar_btn_upload.style.display = 'none'
    textoUploadForm.style.display = 'none'
});

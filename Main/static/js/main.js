window.location.hash = 'inicio'; 

let footerStatus = 0;
let setaStatus = 0;
let dropStatus = 0;

function scrollFooter() {
    setTimeout(() => {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    }, 0);
}
function toggleFooterSize() {
    const footer = document.getElementById('footer');
    const seta = document.getElementById('seta');
    const segundoFooter = document.querySelector('.segundoFooter');
    const tooltip = document.getElementById('tooltipSeta');


    // Adicione um listener para quando a transição terminar
    footer.addEventListener('transitionend', function onTransitionEnd() {
        scrollFooter(); // Executa o scroll assim que a transição terminar
        footer.removeEventListener('transitionend', onTransitionEnd); // Remove o listener após a primeira execução
    });

    if (footerStatus === 0) {
        footer.style.height = '30vh';
        segundoFooter.style.display = 'flex';
        footerStatus = 1;
        tooltip.textContent = "Clique para Fechar";
    } else if (footerStatus === 1) {
        footer.style.height = '5vh';
        segundoFooter.style.display = 'none';
        footerStatus = 0;
        tooltip.textContent = "Clique para Expandir";
    }

    if (setaStatus === 0) {
        seta.style.transform = 'rotate(180deg)';
        setaStatus = 1;
    } else if (setaStatus === 1) {
        seta.style.transform = 'rotate(0deg)';
        setaStatus = 0;
    }
}



function resetShadows() {
    const labels = document.querySelectorAll('.trocaPag');
    labels.forEach(label => {
        label.style.boxShadow = 'none';
    });
}


document.querySelector('.welcomeDiv').style.display = 'flex';
document.querySelector('.graficDiv').style.display = 'none';
document.querySelector('.uploadDiv').style.display = 'none';

function homeFunc() {
    resetShadows();
    document.querySelector('.welcomeDiv').style.display = 'flex';
    document.querySelector('.graficDiv').style.display = 'none';
    document.querySelector('.uploadDiv').style.display = 'none';
    document.querySelector('.trocaPag:nth-child(1)').style.boxShadow = 'inset 0px -0.2vh 0px 0px var(--color-crimson)';
    window.location.hash = 'inicio';
    document.title = "Sen.AI - Ínicio";
}

function graficFunc() {
    resetShadows();
    document.querySelector('.welcomeDiv').style.display = 'none';
    document.querySelector('.graficDiv').style.display = 'flex';
    document.querySelector('.uploadDiv').style.display = 'none';
    document.querySelector('.trocaPag:nth-child(2)').style.boxShadow = 'inset 0px -0.2vh 0px 0px var(--color-crimson)';
    window.location.hash = 'graficos';
    document.title = "Sen.AI - Gráficos";
    fecharPopup()
}
function fecharPopup(){
    const fundoCinza = document.getElementById('fundoCinza');
    const popupCheck = document.getElementById('popupCheck');
    const popupInfo = document.getElementById('popupInfo');
    const popupResultado = document.querySelector('.divResultado');
    fundoCinza.classList.remove('fundoCinza');
    popupCheck.style.display = 'none'
    popupInfo.style.display = 'none'
    popupResultado.style.display = 'none'
}

function confirmarPeca(){
    fecharPopup()
}

function mostrarPopup(){
    const fundoCinza = document.getElementById('fundoCinza');
    const popup = document.getElementById('popupCheck');
    fundoCinza.classList.add('fundoCinza');
    popup.style.display = 'grid'
}
function mostrarPopupInfo(){
    const fundoCinza = document.getElementById('fundoCinza');
    const popup = document.getElementById('popupInfo');
    
    fundoCinza.classList.add('fundoCinza');
    popup.style.display = 'flex';
    popup.classList.add('show');
}

function ativarDivResposta(){
    fecharPopup()
    fundoCinza.classList.add('fundoCinza');
    document.querySelector('.divResultado').style.display = 'flex';
}
function respostaPecaBoa(){
    ativarDivResposta();
    document.getElementById('respostaPecaBoa').style.display = 'flex';
    document.getElementById('respostaPecaRuim').style.display = 'none';
}
function respostaPecaRuim(){
    ativarDivResposta();
    document.getElementById('respostaPecaRuim').style.display = 'flex';
    document.getElementById('respostaPecaBoa').style.display = 'none';
}

function uploadFunc() {
    resetShadows();
    document.querySelector('.welcomeDiv').style.display = 'none';
    document.querySelector('.graficDiv').style.display = 'none';
    document.querySelector('.uploadDiv').style.display = 'flex';
    document.querySelector('.trocaPag:nth-child(3)').style.boxShadow = 'inset 0px -0.2vh 0px 0px var(--color-crimson)';
    window.location.hash = 'upload';
    document.title = "Sen.AI - Uploud";
    fecharPopup();
}

function dropdownUser() {
    const menuUser = document.querySelector('.menuUser');

    if (dropStatus === 0) {
        menuUser.style.top = '0%';
        dropStatus = 1
    } else if (dropStatus === 1) {
        menuUser.style.top = '-120%';
        dropStatus = 0
    }
}

function toggleDarkMode() {
    const body = document.body;
    const toggle = document.getElementById('toggle-theme');
    const imageWelcome = document.getElementById('welcomeImg');
    const imageLogo = document.getElementById('logoImg');
    const imageUser = document.getElementById('userImg');
    const imageUpload = document.getElementById('uploadImg');
    const imageGraficLight = document.getElementById('graficImage');
    const imageGraficDark = document.getElementById('graficImageDark')
    const imgLogoPopup = document.querySelector('.imgLogoPopup');

    if (toggle.checked) {
        body.classList.add('dark-mode');
        imageWelcome.src = "/static/images/welcomeImageDark.png"
        imageLogo.src = "/static/images/Logo_SenAI_NovaDark.png"
        imageUser.src = "/static/images/UserImgDark.png"
        imageUpload.src = "/static/images/UploadImgDark.png"
        imageGraficLight.style = "display: none"
        imageGraficDark.style = "display: grid"
        imgLogoPopup.src = "/static/images/Logo_SenAI_NovaDark.png"
    } else {
        body.classList.remove('dark-mode');
        imageWelcome.src = "/static/images/welcomeImage.png"
        imageLogo.src = "/static/images/Logo_SenAI_NovaB.png"
        imageUser.src = "/static/images/UserImgRed.png"
        imageUpload.src = "/static/images/UploadImg.png"
        imageGraficLight.style = "display: grid"
        imageGraficDark.style = "display: none"
        imgLogoPopup.src = "/static/images/Logo_SenAI_NovaB.png"
    }
}
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse, urldefrag
from concurrent.futures import ThreadPoolExecutor, as_completed
import os



# Função para verificar se o conteúdo é relevante para "linhas de crédito"
def conteudo_relevante(texto):
    palavras_chave = [
        "linha de crédito", "linhas de crédito", "crédito para projeto", "financiamento",
        "regras de crédito", "condições de crédito", "empréstimo para projeto", "crédito empresarial"
    ]

    return any(palavra in texto.lower() for palavra in palavras_chave)


# Função para filtrar URLs principais
def url_principal(url):
    parsed_url = urlparse(url)

    # Excluir URLs com fragmentos ou parâmetros de consulta
    if parsed_url.fragment or parsed_url.query:
        return False

    # Verificar se a URL contém números (como em IDs dinâmicos) ou caminhos muito longos
    path = parsed_url.path.strip("/")
    if any(char.isdigit() for char in path.split("/")) or len(path.split("/")) > 2:
        return False

    return True


# Função para buscar o conteúdo de uma URL específica
def buscar_conteudo(url):
    print(f"Vasculhando: {url}")

    try:
        response = requests.get(url, timeout=10)  # Adicionando timeout para evitar longas esperas
        if response.status_code != 200:
            print(f"Erro ao acessar a URL: {response.status_code}")
            return False, set()

        # Forçar a codificação correta da resposta
        response.encoding = response.apparent_encoding

    except Exception as e:
        print(f"Erro ao tentar acessar a URL: {e}")
        return False, set()

    try:
        # Usar o parser 'lxml' como alternativa se houver problemas com 'html.parser'
        soup = BeautifulSoup(response.content, 'lxml')

    except Exception as e:
        print(f"Erro ao tentar parsear o HTML: {e}")
        return False, set()

    conteudo_relevante_encontrado = False
    for tag in soup.find_all('div'):
        texto = tag.get_text(strip=True)
        if len(texto) < 100:
            continue

        if conteudo_relevante(texto):
            conteudo_relevante_encontrado = True
            break

    links_internos = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        url_absoluta = urljoin(url, href)

        # Filtrar e adicionar apenas URLs principais
        if urlparse(url_absoluta).netloc == urlparse(url).netloc and url_principal(url_absoluta):
            links_internos.add(url_absoluta)

    return conteudo_relevante_encontrado, links_internos


# Função principal que executa o scraping e salva as URLs com conteúdo relevante em JSON
def buscar_e_atualizar_json(url, tempo_maximo=900):
    start_time = time.time()
    visitados = set()
    urls_relevantes = set()
    links_para_visitar = {url}

    with ThreadPoolExecutor(max_workers=10) as executor:
        while links_para_visitar:
            futuros = {executor.submit(buscar_conteudo, link): link for link in links_para_visitar}
            links_para_visitar = set()

            for futuro in as_completed(futuros):
                link = futuros[futuro]
                conteudo_relevante_encontrado, links_internos = futuro.result()

                if conteudo_relevante_encontrado:
                    urls_relevantes.add(link)

                # Filtrar URLs já visitadas e adicionar novas URLs principais
                novos_links = links_internos - visitados
                visitados.update(novos_links)
                links_para_visitar.update(novos_links)

            # Verifica o tempo decorrido
            elapsed_time = time.time() - start_time
            if elapsed_time > tempo_maximo:
                print("Tempo máximo de execução atingido.")
                break

    # Obter o caminho absoluto do script atual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construir o caminho absoluto para o arquivo JSON
    json_path = os.path.join(script_dir, 'links_aneel.json')

    # Salvar em JSON usando o caminho absoluto
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(list(urls_relevantes), f, ensure_ascii=False, indent=4)

    print(f"URLs vasculhadas e URLs relevantes salvas em '{json_path}'.")


# Exemplo de uso: URL e tempo máximo de execução em segundos (por exemplo, 1800 segundos para 30 minutos)
url = 'https://www.gov.br/anp/pt-br/assuntos/pesquisa-desenvolvimento-e-inovacao/investimentos-em-pd-i'  # Altere o link aqui dentro para o qual você deseja fazer a busca
tempo_maximo = 900  # Tempo máximo de execução em segundos (30min)
buscar_e_atualizar_json(url, tempo_maximo)
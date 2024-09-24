import requests
from bs4 import BeautifulSoup
import json

def conteudo_relevante(texto):
    palavras_chave = [
        "linha de crédito", "linhas de crédito", "crédito para projeto", "financiamento",
        "regras de crédito", "condições de crédito", "empréstimo para projeto", "crédito empresarial"
    ]
    for palavra in palavras_chave:
        if palavra in texto.lower():
            return True
    return False

def buscar_conteudo(url):
    print(f"Vasculhando: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Erro ao acessar a URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao tentar acessar a URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    texto_relevante = []
    for tag in soup.find_all('div'):
        texto = tag.get_text(strip=True)
        if len(texto) < 100:
            continue
        if conteudo_relevante(texto):
            texto_relevante.append(texto)

    if texto_relevante:
        return ' '.join(texto_relevante)
    return None

def buscar_e_atualizar_json():
    urls_com_conteudo_relevante = []

    try:
        with open('LINKS/links_fapesp.json', 'r', encoding='utf-8') as f:
            urls = json.load(f)
    except FileNotFoundError:
        print("Arquivo 'links.json' não encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON.")
        return

    for url in urls:
        conteudo_relevante_encontrado = buscar_conteudo(url)
        if conteudo_relevante_encontrado:
            urls_com_conteudo_relevante.append({
                "url": url,
                "conteudo": conteudo_relevante_encontrado
            })

    with open('DADOS/conteudo_fapesp.json', 'w', encoding='utf-8') as f:
        json.dump(urls_com_conteudo_relevante, f, ensure_ascii=False, indent=4)

    print(f"Processo concluído. URLs e conteúdos relevantes salvos em 'conteudo.json'.")

buscar_e_atualizar_json()
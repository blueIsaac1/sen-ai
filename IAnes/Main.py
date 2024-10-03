import json
import google.generativeai as genai
import os
import time
from google.api_core import exceptions as google_exceptions

# Configuração da chave da API
api_key = 'AIzaSyCdUc8hHD_Uf6yior7ujtW5wvPYMepoh5I'  # Substitua pela sua chave de API
os.environ["API_KEY"] = api_key
genai.configure(api_key=os.environ["API_KEY"])


# Função para carregar o conteúdo das páginas a partir de um arquivo JSON
def carregar_conteudo(pasta):
    todos_conteudos = []
    for arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, arquivo)
        if os.path.isfile(caminho_completo):
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                try:
                    conteudo = json.load(f)
                    todos_conteudos.append({"arquivo": arquivo, "conteudo": conteudo})
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar JSON do arquivo {arquivo}. Pulando...")
    return todos_conteudos

# Função para obter inputs do usuário
def obter_parametros_usuario():
    nome = input("Nome da pessoa: ")
    projeto = input("Nome do projeto: ")
    tema = input("Tema do projeto: ")
    area = input("Área de atuação: ")
    esboco = input("Esboço - Como será o projeto: ")
    orcamento = input("Orçamento esperado: ")
    extensao = input("Extensão geográfica (Regional, Nacional, Mundial): ")

    return {
        "nome": nome,
        "projeto": projeto,
        "tema": tema,
        "area": area,
        "esboco": esboco,
        "orcamento": orcamento,
        "extensao": extensao
    }


# Função para obter análise da API Gemini
def get_gemini_analysis_with_retry(content, user_inputs, max_retries=5, initial_delay=1):
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Analise o seguinte conteúdo com base nas seguintes entradas do usuário:\n\nConteúdo: {content}\n\nEntradas do usuário: {user_inputs}\n\nForneça uma pontuação de relevância entre 0 e 10 e uma breve descrição da relevância."
            response = model.generate_content(prompt)
            return response.text
        except google_exceptions.ResourceExhausted:
            if attempt == max_retries - 1:
                print(f"Falha após {max_retries} tentativas. Retornando análise padrão.")
                return "0\nNão foi possível analisar devido a limitações da API."
            delay = initial_delay * (2 ** attempt)
            print(f"Limite de recursos atingido. Tentando novamente em {delay} segundos...")
            time.sleep(delay)
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return "0\nErro na análise."

def analise_page(content, inputs):
    analysis = get_gemini_analysis_with_retry(content, inputs)

    try:
        analysis_lines = analysis.split('\n')
        score = float(analysis_lines[0].split(':')[1].strip()) if ':' in analysis_lines[0] else float(analysis_lines[0])
        description = analysis_lines[1].strip()
    except Exception as e:
        print(f"Erro ao processar a análise: {e}")
        score = 0
        description = "Descrição não disponível"

    return score, description

def recomenda_investimento(conteudos, inputs):
    best_option = None
    best_score = 0
    best_url = None

    for pagina in conteudos:
        arquivo = pagina['arquivo']
        content = pagina['conteudo']

        # Verifica se o conteúdo é uma lista e pega o primeiro item se for
        if isinstance(content, list) and len(content) > 0:
            item = content[0]
        else:
            item = content

        # Converte o item para string, caso seja um dicionário
        content_str = json.dumps(item) if isinstance(item, dict) else str(item)

        score, description = analise_page(content_str, inputs)
        print(f"Arquivo: {arquivo} - Score: {score}.")

        if score > best_score:
            best_score = score
            best_option = arquivo
            # Tenta obter a URL do item, se for um dicionário
            best_url = item.get('url', 'URL não encontrada') if isinstance(item, dict) else 'URL não encontrada'

        time.sleep(1)  # Pequeno delay entre as chamadas para evitar sobrecarga

    return best_option, best_url

def main():
    pasta_dados = 'DADOS'  # Nome da pasta contendo os arquivos JSON
    dados_paginas = carregar_conteudo(pasta_dados)
    user_inputs = obter_parametros_usuario()
    recommendation, url = recomenda_investimento(dados_paginas, user_inputs)

    if recommendation:
        print(f"Melhor opção de investimento encontrada: {url}")
    else:
        print("Nenhuma opção de investimento adequada foi encontrada.")

if __name__ == "__main__":
    main()
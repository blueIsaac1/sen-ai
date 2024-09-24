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

def obter_parametros_usuario():
    nome = input("Nome da pessoa: ")
    projeto = input("Nome do projeto: ")

    # Menu de seleção para a área
    print("Escolha a área de atuação:")
    opcoes_area = ['tecnologia', 'agro', 'metalurgia', 'mecanica', 'robotica', 'automação', 'eletrica']
    for i, opcao in enumerate(opcoes_area, start=1):
        print(f"{i}. {opcao}")

    escolha_area = int(input("Digite o número da opção desejada: "))
    area = opcoes_area[escolha_area - 1] if 1 <= escolha_area <= len(opcoes_area) else "Opção inválida"

    esboco = input("Esboço - Como será o projeto: ")
    orcamento = input("Orçamento esperado: ")

    # Menu de seleção para a extensão geográfica
    print("Escolha a extensão geográfica:")
    opcoes_extensao = ['Regional', 'Nacional', 'Mundial']
    for i, opcao in enumerate(opcoes_extensao, start=1):
        print(f"{i}. {opcao}")

    escolha_extensao = int(input("Digite o número da opção desejada: "))
    extensao = opcoes_extensao[escolha_extensao - 1] if 1 <= escolha_extensao <= len(opcoes_extensao) else "Opção inválida"

    return {
        "nome": nome,
        "projeto": projeto,
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
    scores = []
    urls = []

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

        if score is not None:  # Certifica-se de que o score não é None
            scores.append(score)
            urls.append(item.get('url', 'URL não encontrada') if isinstance(item, dict) else 'URL não encontrada')

        time.sleep(1)  # Pequeno delay entre as chamadas para evitar sobrecarga

    if not scores:
        return None, None  # Retorna None para ambos se não houver scores

    # Verifica se todos os scores são 0
    if all(score == 0 for score in scores):
        print("Não há linhas de crédito disponíveis para este projeto.")
        return None, None

    # Encontra os maiores scores únicos
    highest_scores = sorted(set(scores), reverse=True)
    
    # Obtém as URLs correspondentes ao maior score
    best_urls = [urls[i] for i in range(len(scores)) if scores[i] == highest_scores[0]]

    # Imprime o maior score e suas URLs
    print(f"Melhor opção de linha de crédito: {best_urls}")

    # Para o segundo maior score, obtém as URLs correspondentes
    second_best_urls = []
    if len(highest_scores) > 1:
        second_best_urls = [urls[i] for i in range(len(scores)) if scores[i] == highest_scores[1]]
    
    # Imprime o segundo maior score e suas URLs, se existirem
    if second_best_urls:
        print(f"Segunda melhor opção de linha de crédito: {second_best_urls}")

    return highest_scores[0], best_urls

def main():
    pasta_dados = 'DADOS'  # Nome da pasta contendo os arquivos JSON
    dados_paginas = carregar_conteudo(pasta_dados)
    user_inputs = obter_parametros_usuario()
    recommendation, best_urls = recomenda_investimento(dados_paginas, user_inputs)

if __name__ == "__main__":
    main()

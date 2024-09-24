import pickle
import google.generativeai as genai
import os
import time
from google.api_core import exceptions as google_exceptions

api_key = 'AIzaSyCdUc8hHD_Uf6yior7ujtW5wvPYMepoh5I'  # Substitua pela sua chave de API
os.environ["API_KEY"] = api_key
genai.configure(api_key=os.environ["API_KEY"])

def carregar_dados_preprocessados():
    with open('testetreino/dados_preprocessados.pkl', 'rb') as f:
        return pickle.load(f)

# Adicione esta função
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


def recomenda_investimento(dados_preprocessados, inputs):
    best_option = None
    best_score = 0
    best_url = None

    for arquivo, dados in dados_preprocessados.items():
        content = dados['analise']
        score, description = analise_page(content, inputs)
        print(f"Arquivo: {arquivo} - Score: {score} - Descrição: {description}")

        if score > best_score:
            best_score = score
            best_option = arquivo
            best_url = dados['url']

        time.sleep(1)  # Pequeno delay entre as chamadas para evitar sobrecarga

    return best_option, best_url

def main():
    dados_preprocessados = carregar_dados_preprocessados()
    user_inputs = obter_parametros_usuario()
    recommendation, url = recomenda_investimento(dados_preprocessados, user_inputs)

    if recommendation:
        print(f"Melhor opção de investimento encontrada: {url}")
    else:
        print("Nenhuma opção de investimento adequada foi encontrada.")

if __name__ == "__main__":
    main()
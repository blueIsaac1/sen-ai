import json
import os
import pickle
from tqdm import tqdm
import google.generativeai as genai

# Configuração da chave da API
api_key = 'AIzaSyCdUc8hHD_Uf6yior7ujtW5wvPYMepoh5I'
os.environ["API_KEY"] = api_key
genai.configure(api_key=os.environ["API_KEY"])

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

def analisar_conteudo(conteudo):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Analise o seguinte conteúdo e forneça um resumo conciso dos principais tópicos e palavras-chave:\n\n{conteudo}"
    response = model.generate_content(prompt)
    return response.text

def preprocessar_dados(pasta_dados):
    dados_preprocessados = {}
    conteudos = carregar_conteudo(pasta_dados)
    
    for item in tqdm(conteudos, desc="Pré-processando arquivos"):
        arquivo = item['arquivo']
        conteudo = item['conteudo']
        
        if isinstance(conteudo, list) and len(conteudo) > 0:
            item_conteudo = conteudo[0]
        else:
            item_conteudo = conteudo
        
        content_str = json.dumps(item_conteudo) if isinstance(item_conteudo, dict) else str(item_conteudo)
        analise = analisar_conteudo(content_str)
        
        url = item_conteudo.get('url', 'URL não encontrada') if isinstance(item_conteudo, dict) else 'URL não encontrada'
        
        dados_preprocessados[arquivo] = {
            'url': url,
            'analise': analise
        }
    
    with open('testetreino/dados_preprocessados.pkl', 'wb') as f:
        pickle.dump(dados_preprocessados, f)

if __name__ == "__main__":
    pasta_dados = 'DADOS'
    preprocessar_dados(pasta_dados)
    print("Pré-processamento concluído. Dados salvos em 'dados_preprocessados.pkl'")
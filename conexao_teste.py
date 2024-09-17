import sqlite3
import pandas as pd
import re
import matplotlib.pyplot as plt
from datetime import datetime as tm
today = tm.now().date()

try:
    # Conectar ao banco de dados e consultar dados
    conn = sqlite3.connect("./db.sqlite3")
    conn.close()
    print('conectado')
except ValueError as e:
    print('erro', e)
def grafico_consulta_pandas_today():
    try:
        conn = sqlite3.connect("./db.sqlite3")
        query = """
        SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
        FROM Main_imageprediction a
        JOIN Main_infospecas b ON a.peca_id = b.idPeca
        WHERE DATE(a.timestamp) = DATE('now');
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if 'class_label' in df.columns:
            pivot_table = df.pivot_table(columns='class_label', aggfunc='size', fill_value=0)
            # Criar o gráfico
            fig, ax = plt.subplots(figsize=(6, 5))
            pivot_table.plot(kind='bar', stacked=False, color=['#f49494', '#ec1c24'], ax=ax)
            # Configurar labels e título
            ax.set_xlabel('Bom | Ruim')
            ax.set_title('Número de Eventos por Nome da Peça e Situação')
            # Ajustar o limite do eixo y baseado no valor máximo
            max_value = pivot_table.values.max()
            ax.set_ylim(0, max_value + 4)  # Adiciona uma margem de 10%
            # Configurar a rotação dos ticks no eixo x e ajustar layout
            plt.xticks(rotation=0)
            plt.tight_layout()
            # Salvar o gráfico em um arquivo
            plt.savefig('./figs/fig_today.png')
            plt.close(fig)
        else:
            print("A coluna 'class_label' não foi encontrada no DataFrame.")
            print(df)
    except ValueError as e:
        print(f"Erro ao consultar o banco de dados: {e}")



# PIZZA
def grafico_pizza_pandas_today():
    conn = sqlite3.connect("./db.sqlite3")
    # Consulta SQL para buscar os dados
    query = """
    SELECT a.id, a.class_label, a.timestamp, b.idPeca, b.nomePeca
    FROM Main_imageprediction a
    JOIN Main_infospecas b ON a.peca_id = b.idPeca
    WHERE DATE(a.timestamp) = DATE('now');
    """
    # Ler os dados em um DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    # Verificar se as colunas 'situPeca' e 'nomePeca' estão presentes
    if 'class_label' in df.columns and 'nomePeca' in df.columns:
        # Agregar os dados por nome da peça e situação
        situ_counts = df.groupby('nomePeca')['class_label'].value_counts().unstack().fillna(0)
        # Plotar um gráfico de pizza para cada peça
        for piece in situ_counts.index:
            plt.figure(figsize=(4, 5))
            situ_counts.loc[piece].plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=['#f49494', '#ec1c24'])
            # Definir propriedades do título
            plt.title(
                f'Distribuição da Situação para {piece}',
                fontsize=16,  # Ajustar o tamanho da fonte para que o texto caiba bem
                fontweight='bold',
                color='#000000',  # Alterar a cor do título para preto para melhor contraste
                family='Arial'
            )
            plt.tight_layout()
            # Salvar a figura com fundo transparente e ajustada ao conteúdo
            plt.savefig(f'./figs/situ_pie_chart_today.png', transparent=True, bbox_inches='tight', pad_inches=0.1)
            plt.close()
    else:
        print("As colunas 'situPeca' e/ou 'nomePeca' não foram encontradas no DataFrame.")
        print(df)

def consulta_label():
    grafico_consulta_pandas_today()
    grafico_pizza_pandas_today()
    conn = sqlite3.connect("./db.sqlite3")
    cursor = conn.cursor()  # Cria um cursor para executar comandos SQL

    # Consulta para selecionar o último item inserido
    query = """
    SELECT class_label
    FROM Main_imageprediction
    ORDER BY id DESC
    LIMIT 1
    """
    
    cursor.execute(query)  # Executa a consulta
    last_label = cursor.fetchone()  # Obtém o último registro
    conn.close()  # Fecha a conexão

    

    return re.sub(r'[^a-zA-Z\s]', '', last_label[0])

# Chamada da função
popup_message = f"Sucesso: {consulta_label()}"
print(popup_message)
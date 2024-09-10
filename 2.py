import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

try:
    # Conectar ao banco de dados e consultar dados
    conn = sqlite3.connect("./db.sqlite3")
    query = """
    SELECT a.idLog, a.situPeca, a.idUsuario, a.datahora, a.idPeca_id, b.nomePeca
    FROM Main_analisepeca a
    JOIN Main_infospecas b on a.idPeca_id = b.idPeca;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Verificar se a coluna 'nomePeca' está presente
    if 'nomePeca' in df.columns:
        # Criar a tabela dinâmica
        pivot_table = df.pivot_table(index='nomePeca', columns='situPeca', aggfunc='size', fill_value=0)
        
        # Criar o gráfico
        fig, ax = plt.subplots(figsize=(10, 8))
        pivot_table.plot(kind='bar', stacked=False, ax=ax)

        # Ajustar rótulos e título
        ax.set_xlabel('(1 = Bom | 2 = Ruim)')
        ax.set_ylabel('Número de Eventos')
        ax.set_title('Número de Eventos por Nome da Peça e Situação')
        ax.legend(title='Situação da Peça')
        plt.xticks(rotation=0)

        # Ajustar limite do eixo y para acomodar todos os dados
        current_ylim = ax.get_ylim()
        max_value = pivot_table.values.max()
        ax.set_ylim(0, max_value + 4)  # Adiciona um buffer de 10% no topo

        # Ajustar layout e mostrar o gráfico
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # Ajustar margens se necessário
        plt.tight_layout()
        plt.savefig('./figs/fig.png')
    else:
        print("A coluna 'nomePeca' não foi encontrada no DataFrame.")
        print(df)

except ValueError as e:
    print(f"Erro ao consultar o banco de dados: {e}")

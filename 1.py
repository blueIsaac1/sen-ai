import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

# Connect to SQLite database
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("./db.sqlite3")

# Consulta SQL para buscar os dados
query = """
SELECT a.idLog, a.situPeca, a.idUsuario, a.datahora, a.idPeca_id, b.nomePeca
FROM Main_analisepeca a
JOIN Main_infospecas b on a.idPeca_id = b.idPeca;
"""

# Ler os dados em um DataFrame
df = pd.read_sql_query(query, conn)
conn.close()

# Verificar se as colunas 'situPeca' e 'nomePeca' estão presentes
if 'situPeca' in df.columns and 'nomePeca' in df.columns:
    # Agregar os dados por nome da peça e situação
    situ_counts = df.groupby('nomePeca')['situPeca'].value_counts().unstack().fillna(0)

    # Plotar um gráfico de pizza para cada peça
    for piece in situ_counts.index:
        plt.figure(figsize=(4, 5))
        situ_counts.loc[piece].plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=['#1f77b4', '#ff7f0e'])
        
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
        plt.savefig(f'./figs/situ_pie_chart.png', transparent=True, bbox_inches='tight', pad_inches=0.1)
        plt.close()
else:
    print("As colunas 'situPeca' e/ou 'nomePeca' não foram encontradas no DataFrame.")
    print(df, 'oi')

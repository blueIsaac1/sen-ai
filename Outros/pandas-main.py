import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Função para exibir o menu e processar a entrada do usuário
def menu_analise(df):
    while True:
        print('\nMenu De Análise:\n1 - Análise Descritiva\n2 - Análise de Frequência\n3 - Tendências Temporais\n4 - Relação entre Colunas\n5 - Análise por Agrupamento\n6 - Visualização de Relacionamentos\n0 - Sair')
        try:
            deF = int(input('Selecione uma opção: '))
            if deF == 0:
                print('Saindo do menu...')
                break
            elif deF == 1:
                if 'idPeca_id' in df.columns:
                    df['idPeca_id'].hist()
                    plt.xlabel('ID Peça')
                    plt.ylabel('Frequência')
                    plt.title('Distribuição dos IDs das Peças')
                    plt.show()
                else:
                    print("Coluna 'idPeca_id' não encontrada no DataFrame.")
            elif deF == 2:
                if 'situPeca' in df.columns:
                    df['situPeca'].value_counts().plot(kind='bar')
                    plt.xlabel('Situação da Peça')
                    plt.ylabel('Contagem')
                    plt.title('Distribuição das Situações das Peças')
                    plt.show()
                else:
                    print("Coluna 'situPeca' não encontrada no DataFrame.")
            elif deF == 3:
                if 'datahora' in df.columns:
                    df['datahora'] = pd.to_datetime(df['datahora'])
                    df.set_index('datahora', inplace=True)
                    df.resample('D').size().plot()
                    plt.xlabel('Data')
                    plt.ylabel('Número de Eventos')
                    plt.title('Número de Eventos por Dia')
                    plt.show()
                else:
                    print("Coluna 'datahora' não encontrada no DataFrame.")
            elif deF == 4:
                if 'idLog' in df.columns and 'idPeca_id' in df.columns:
                    df.plot.scatter(x='idLog', y='idPeca_id')
                    plt.xlabel('ID Log')
                    plt.ylabel('ID Peça')
                    plt.title('Relação entre ID Log e ID Peça')
                    plt.show()
                else:
                    print("Colunas 'idLog' e/ou 'idPeca_id' não encontradas no DataFrame.")
            elif deF == 5:
                if 'situPeca' in df.columns and 'idPeca_id' in df.columns:
                    df.groupby('situPeca').mean()['idPeca_id'].plot(kind='bar')
                    plt.xlabel('Situação da Peça')
                    plt.ylabel('Média do ID da Peça')
                    plt.title('Média dos IDs das Peças por Situação')
                    plt.show()
                else:
                    print("Colunas 'situPeca' e/ou 'idPeca_id' não encontradas no DataFrame.")
            elif deF == 6:
                if 'situPeca' in df.columns and 'idPeca_id' in df.columns:
                    df.groupby(['situPeca', 'idPeca_id']).size().unstack().plot(kind='bar', stacked=True)
                    plt.xlabel('Situação da Peça')
                    plt.ylabel('Número de Eventos')
                    plt.title('Número de Eventos por Situação e ID da Peça')
                    plt.show()
                else:
                    print("Colunas 'situPeca' e/ou 'idPeca_id' não encontradas no DataFrame.")
            else:
                print('Opção inválida. Por favor, selecione uma opção válida.')
        except ValueError:
            print('Entrada inválida. Por favor, insira um número inteiro.')

# Conectar ao banco de dados SQLite e carregar dados
try:
    conn = sqlite3.connect("C:/Users/CTDEV23/Desktop/isaacctdev-23/django/100-ai-main/djangoMain/db.sqlite3")
    query = """
    SELECT idLog, situPeca, idUsuario, datahora, idPeca_id
    FROM Main_analisepeca;
    """
    df = pd.read_sql_query(query, conn)
except sqlite3.Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    df = pd.DataFrame()
finally:
    if conn:
        conn.close()

# Verificar se o DataFrame não está vazio e exibir menu de análise
if not df.empty:
    print(df)
    menu_analise(df)
else:
    print("O DataFrame está vazio. Verifique a conexão e a consulta SQL.")

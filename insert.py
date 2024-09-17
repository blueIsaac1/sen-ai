import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('db.sqlite3')  # Substitua 'db.sqlite3' pelo nome do seu banco de dados
cursor = conn.cursor()

# Inserir um registro na tabela InfosPecas
nome_peca = "Peca Exemplo"
situ_peca = 1
fornecedor_peca = "Fornecedor Exemplo"

cursor.execute('''
    INSERT INTO Main_infospecas (nomePeca, situPeca, fornecedorPeca)
    VALUES (?, ?, ?)
''', (nome_peca, situ_peca, fornecedor_peca))

# Obter o ID da peça inserida
id_peca = cursor.lastrowid

# Inserir um registro na tabela AnalisePeca
id_usuario = 1  # Substitua pelo ID do usuário que você deseja
situ_peca_analise = 1

# cursor.execute('''
#     INSERT INTO app_analisepeca (idPeca_id, situPeca, IdUsuario)
#     VALUES (?, ?, ?)
# ''', (id_peca, situ_peca_analise, id_usuario))

# Confirmar as transações
conn.commit()

# Fechar a conexão
conn.close()

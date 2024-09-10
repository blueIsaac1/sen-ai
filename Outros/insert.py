import sqlite3

# Conectar ao banco de dados (ou criá-lo se não existir)
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Comando SQL para criação das tabelas
sql_create_tables = """
CREATE TABLE InfosPecas (
    idPeca INTEGER PRIMARY KEY AUTOINCREMENT,
    nomePeca TEXT UNIQUE NOT NULL,
    situPeca INTEGER NOT NULL,
    fornecedorPeca TEXT UNIQUE NOT NULL
);
"""
sql2 = """
CREATE TABLE AnalisePeca (
    idLog INTEGER PRIMARY KEY AUTOINCREMENT,
    idPeca INTEGER,
    situPeca INTEGER,
    IdUsuario INTEGER,
    datahora REAL NOT NULL,
    FOREIGN KEY (idPeca) REFERENCES InfosPecas(idPeca),
    FOREIGN KEY (situPeca) REFERENCES InfosPecas(situPeca),
    FOREIGN KEY (idUsuario) REFERENCES auth_user(id)
);
"""
# Executar o comando SQL
cursor.executescript(sql_create_tables)

# Confirmar a transação (fazer o commit)
conn.commit()

# Fechar a conexão com o banco de dados
conn.close()

print("Criação das tabelas concluída com sucesso.")

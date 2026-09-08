import sqlite3

# Cria ou abre o banco de dados
conexao = sqlite3.connect("duelo_garagem.db")

cursor = conexao.cursor()

# Cria a tabela de carros
cursor.execute("""
CREATE TABLE IF NOT EXISTS carros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    marca TEXT NOT NULL,
    potencia INTEGER NOT NULL,
    velocidade INTEGER NOT NULL,
    zero_cem REAL NOT NULL
)
""")

# Cadastra os carros
carros = [
    ("Ferrari 488 GTB", "Ferrari", 670, 330, 3.0),
    ("Lamborghini Huracán", "Lamborghini", 640, 325, 2.9),
    ("Porsche 911 Turbo S", "Porsche", 650, 330, 2.7),
    ("McLaren 720S", "McLaren", 720, 341, 2.9),
    ("Chevrolet Corvette C8", "Chevrolet", 495, 312, 2.9)
]

cursor.execute("SELECT COUNT(*) FROM carros")
quantidade = cursor.fetchone()[0]

if quantidade == 0:
    cursor.executemany("""
    INSERT INTO carros (nome, marca, potencia, velocidade, zero_cem)
    VALUES (?, ?, ?, ?, ?)
    """, carros)

    print("Carros cadastrados com sucesso!")
else:
    print("Os carros já estão cadastrados.")

conexao.commit()
conexao.close()


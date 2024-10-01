import sqlite3

# Função para criar a tabela no banco de dados SQLite
def create_table():
    conn = sqlite3.connect('finances.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT,
                  month TEXT,
                  amount REAL,
                  description TEXT)''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Banco de dados e tabela criados com sucesso.")

import sqlite3

# Создание таблицы аккаунтов, если её не существует
def create_accounts_table():
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(50), pass VARCHAR(50), balance INTEGER DEFAULT 0, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, operation_type VARCHAR(10))')
    conn.commit()
    conn.close()

# Поиск аккаунта по имени и паролю
def find_account(name, password):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    if password:
        cur.execute("SELECT * FROM accounts WHERE name=? AND pass=?", (name, password))
    else:
        cur.execute("SELECT * FROM accounts WHERE name=?", (name,))
    result = cur.fetchone()
    conn.close()
    return result

# Вставка нового аккаунта в базу данных
def insert_account(name, password):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts(name, pass) VALUES (?, ?)", (name, password))
    conn.commit()
    conn.close()

# Обновление баланса аккаунта
def update_balance(name, amount, operation_type):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    if operation_type == 'deposit':
        cur.execute("UPDATE accounts SET balance = balance + ?, timestamp = CURRENT_TIMESTAMP, operation_type = ? WHERE name=?", (amount, operation_type, name))
    elif operation_type == 'withdraw':
        cur.execute("UPDATE accounts SET balance = balance - ?, timestamp = CURRENT_TIMESTAMP, operation_type = ? WHERE name=?", (amount, operation_type, name))
    conn.commit()
    conn.close()

# Получение баланса аккаунта
def get_balance(name):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("SELECT balance FROM accounts WHERE name=?", (name,))
    result = cur.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

# Получение истории операций аккаунта
def get_history(name):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE name=?", (name,))
    results = cur.fetchall()
    conn.close()
    return results

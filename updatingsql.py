import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('money.sql')
cur = conn.cursor()

# Обновляем схему таблицы, добавляя колонку balance
cur.execute("ALTER TABLE accounts ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

# Коммитим изменения и закрываем соединение
conn.commit()
conn.close()

print("Схема базы данных успешно обновлена!")

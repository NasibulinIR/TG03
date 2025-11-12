import sqlite3

conn = sqlite3.connect('bot.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT,
             chat_id INTEGER
             )''')

conn.commit()
conn.close()

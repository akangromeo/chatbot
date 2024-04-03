import sqlite3

def  create_db():
  return sqlite3.connect('db_romeobot.db')

conn = create_db()
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS inbox (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL,
               message TEXT NOT NULL,
               date TIMESTAMP NOT NULL
               )
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS outbox (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL,
               message TEXT NOT NULL,
               date TIMESTAMP NOT NULL

               )
            """)

conn.commit()
conn.close()
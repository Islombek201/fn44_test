import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            full_name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            copies INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_user(telegram_id: int, full_name: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (telegram_id, full_name) VALUES (?, ?)",
        (telegram_id, full_name)
    )
    conn.commit()
    conn.close()

def get_all_books():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, copies FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def search_books(query: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, copies FROM books WHERE title LIKE ?", (f"%{query}%",))
    books = cursor.fetchall()
    conn.close()
    return books

# Fayl ishga tushganda bazani yaratib qo'yadi
init_db()
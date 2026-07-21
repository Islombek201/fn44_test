import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def add_user(telegram_id: int, full_name: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO bot_users (telegram_id, full_name)
            VALUES (%s, %s)
            ON CONFLICT (telegram_id) DO NOTHING;
        """
        cursor.execute(query, (telegram_id, full_name))
        conn.commit()
    except Exception as e:
        print(f"Foydalanuvchini qo'shishda xatolik: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_all_books():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT b.title, a.name, b.available_copies
            FROM books b
            JOIN authors a ON b.author_id = a.id;
        """
        cursor.execute(query)
        books = cursor.fetchall()
        return books
    except Exception as e:
        print(f"Kitoblarni yuklashda xatolik yuz berdi: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def search_books(query_text: str):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT title, available_copies 
            FROM books 
            WHERE title ILIKE %s;
        """
        search_pattern = f"%{query_text}%"

        cursor.execute(query, (search_pattern,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Qidiruvda xatolik yuz berdi: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
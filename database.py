import os
import psycopg2
from dotenv import load_dotenv

# .env faylini yuklaymiz
load_dotenv()

def get_db_connection():
    """Ma'lumotlar bazasiga to'g'ridan-to'g'ri parametrlar bilan ulanish"""
    return psycopg2.connect(
        host="localhost",
        database="test_dp",
        user="postgres",
        password="20102008",
        port=5432
    )

def add_user(telegram_id: int, full_name: str):
    """Foydalanuvchini bot_users jadvaliga qo'shish"""
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
    """Barcha kitoblarni mualliflari bilan bitta JOIN so'rovda o'qib olish"""
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
    """Kitob nomiga qarab qidirish funksiyasi (ILIKE operatori orqali)"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Rasmdagi logikaga mos SQL so'rovi (% belgilari so'zning istalgan joyida qidirish uchun)
        query = """
            SELECT title, available_copies 
            FROM books 
            WHERE title ILIKE %s;
        """
        # %query_text% formatida qidiruv matnini tayyorlaymiz
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
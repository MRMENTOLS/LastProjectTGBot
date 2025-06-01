import sqlite3
import os

DB_NAME = "career.db"

def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS professions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    skills TEXT,
                    salary TEXT,
                    education TEXT,
                    subjects TEXT
                )
            """)
            conn.commit()
        print(f"✅ База данных '{DB_NAME}' успешно создана или уже существует.")
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")

def add_profession_to_db(profession_data, subjects):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO professions 
                (name, description, skills, salary, education, subjects)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profession_data["name"],
                profession_data.get("description", ""),
                ", ".join(profession_data.get("skills", [])),
                profession_data.get("salary", ""),
                ", ".join(profession_data.get("education", [])),
                ", ".join(subjects)
            ))
            conn.commit()
    except Exception as e:
        print(f"❌ Ошибка при добавлении профессии в БД: {e}")

def get_random_profession_from_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM professions ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "skills": row[3].split(", "),
                    "salary": row[4],
                    "education": row[5].split(", "),
                    "subjects": row[6].split(", ")
                }
            return None
    except Exception as e:
        print(f"❌ Ошибка при получении профессии из БД: {e}")
        return None
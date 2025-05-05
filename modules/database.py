import os
import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

from modules.config import DB_PATH, CLASS_DB_PATH

class DatabaseManager:
    def __init__(self, path: str):
        # Подключение к базе данных с поддержкой многопоточности
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Создание таблицы пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                points INTEGER DEFAULT 0,
                registration_date TEXT
            )
        ''')
        # Создание таблицы вопросов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'open',
                created_at TEXT
            )
        ''')
        # Создание таблицы ответов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                responder_id INTEGER,
                answer_type TEXT,
                contact_info TEXT,
                meeting_time TEXT,
                created_at TEXT
            )
        ''')
        # Создание таблицы состояний пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                temp_data TEXT
            )
        ''')
        # Создание таблицы авторизованных контактов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact TEXT UNIQUE,
                added_at TEXT
            )
        ''')
        self.conn.commit()

    def execute(self, query: str, params: tuple = ()):
        # Выполнение SQL-запроса с обработкой ошибок
        try:
            cur = self.cursor.execute(query, params)
            self.conn.commit()
            return cur
        except Exception as e:
            print(f"Database error: {e}")
            raise

    def fetchone(self, query: str, params: tuple = ()):
        # Получение одной записи из базы данных
        return self.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        # Получение всех записей из базы данных
        return self.execute(query, params).fetchall()

    def close(self):
        # Закрытие соединения с базой данных
        self.conn.close()

class ClassDatabaseManager:
    def __init__(self, path: str):
        # Инициализация менеджера базы данных классов
        self.path = path
        self._create_tables()

    def _create_tables(self):
        # Создание таблицы баллов классов
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS class_scores (
                    class_name TEXT PRIMARY KEY,
                    total_score INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def get_scores(self) -> List[Tuple]:
        # Получение списка баллов всех классов
        try:
            if not os.path.exists(self.path):
                return []
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT class_name, total_score FROM class_scores ORDER BY total_score DESC")
                return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching class scores: {e}")
            return []

    def add_score(self, class_name: str, score: int) -> bool:
        # Добавление баллов классу (создание или обновление)
        try:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT total_score FROM class_scores WHERE class_name = ?", (class_name,))
                result = cursor.fetchone()
                
                if result:
                    # Обновление существующего класса
                    new_score = result[0] + score
                    cursor.execute(
                        "UPDATE class_scores SET total_score = ? WHERE class_name = ?",
                        (new_score, class_name)
                    )
                else:
                    # Создание нового класса
                    cursor.execute(
                        "INSERT INTO class_scores (class_name, total_score) VALUES (?, ?)",
                        (class_name, score)
                    )
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding score: {e}")
            return False

# Глобальные переменные для доступа к базам данных
user_db = None
class_db = None

def init_databases():
    # Инициализация баз данных пользователей и классов
    global user_db, class_db
    user_db = DatabaseManager(DB_PATH)
    class_db = ClassDatabaseManager(CLASS_DB_PATH)

def register_user(user_id: int, username: str):
    # Регистрация нового пользователя
    reg_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    user_db.execute(
        'INSERT OR IGNORE INTO users(user_id, username, registration_date) VALUES(?,?,?)', 
        (user_id, username, reg_date)
    )

def get_username(user_id: int) -> Optional[str]:
    # Получение и��ени пользователя по ID
    result = user_db.fetchone('SELECT username FROM users WHERE user_id = ?', (user_id,))
    return result[0] if result else None

def save_question(user_id: int, title: str, description: str) -> int:
    # Сохранение нового вопроса и очистка состояния пользователя
    cursor = user_db.execute(
        'INSERT INTO questions(author_id, title, description, status, created_at) VALUES(?,?,?,?,?)',
        (user_id, title, description, 'open', datetime.now().strftime('%Y-%m-%d %H:%M'))
    )
    user_db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))
    return cursor.lastrowid

def get_open_questions() -> List[Tuple]:
    # Получение списка открытых вопросов
    return user_db.fetchall('''
        SELECT q.id, q.title, COALESCE(u.username, 'Аноним')
        FROM questions q
        LEFT JOIN users u ON q.author_id = u.user_id
        WHERE LOWER(q.status) = 'open'
        ORDER BY q.created_at DESC
    ''')

def get_question_details(question_id: int) -> Optional[Dict[str, Any]]:
    # Получение детальной информации о вопросе
    question_data = user_db.fetchone('''
        SELECT q.id, q.author_id, q.title,
               COALESCE(q.description, 'Нет описания'),
               q.status, q.created_at,
               COALESCE(u.username, 'Аноним')
        FROM questions q
        LEFT JOIN users u ON q.author_id = u.user_id
        WHERE q.id = ?
    ''', (question_id,))
    
    if not question_data:
        return None
        
    return {
        'id': question_data[0],
        'author_id': question_data[1],
        'title': question_data[2],
        'description': question_data[3],
        'status': question_data[4].lower(),
        'created_at': question_data[5],
        'author': question_data[6]
    }

def close_question(question_id: int) -> None:
    # Закрытие вопроса (изменение статуса)
    user_db.execute('UPDATE questions SET status = "closed" WHERE id = ?', (question_id,))

def save_online_answer(question_id: int, user_id: int, contact: str) -> None:
    # Сохранение онлайн-ответа и закрытие вопроса
    user_db.execute(
        'INSERT INTO answers(question_id, responder_id, answer_type, contact_info, created_at) VALUES(?,?,?,?,?)',
        (question_id, user_id, 'online', contact, datetime.now().strftime('%Y-%m-%d %H:%M'))
    )
    close_question(question_id)

def save_offline_answer(question_id: int, user_id: int, meeting_time: str) -> None:
    # Сохранение офлайн-ответа и закрытие вопроса
    user_db.execute(
        'INSERT INTO answers(question_id, responder_id, answer_type, meeting_time, created_at) VALUES(?,?,?,?,?)',
        (question_id, user_id, 'offline', meeting_time, datetime.now().strftime('%Y-%m-%d %H:%M'))
    )
    close_question(question_id)

def save_state(user_id: int, data: str) -> None:
    # Сохранение временного состояния пользователя
    user_db.execute('INSERT OR REPLACE INTO user_states(user_id, temp_data) VALUES(?,?)', (user_id, data))

def get_state(user_id: int) -> Optional[str]:
    # Получение временного состояния пользователя
    row = user_db.fetchone('SELECT temp_data FROM user_states WHERE user_id=?', (user_id,))
    return row[0] if row else None

def clear_state(user_id: int) -> None:
    # Очистка временного состояния пользователя
    user_db.execute('DELETE FROM user_states WHERE user_id = ?', (user_id,))

def add_authorized_contact(contact: str) -> bool:
    # Добавление контакта в список авторизованных
    try:
        user_db.execute(
            'INSERT INTO authorized_contacts(contact, added_at) VALUES(?,?)',
            (contact, datetime.now().strftime('%Y-%m-%d %H:%M'))
        )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception:
        return False

def remove_authorized_contact(contact: str) -> bool:
    # Удаление контакта из списка авторизованных
    cursor = user_db.execute('DELETE FROM authorized_contacts WHERE contact = ?', (contact,))
    return cursor.rowcount > 0

def is_contact_authorized(contact: str) -> bool:
    # Проверка авторизации контакта
    result = user_db.fetchone('SELECT id FROM authorized_contacts WHERE contact = ?', (contact,))
    return result is not None

def get_authorized_contacts() -> List[str]:
    # Получение списка всех авторизованных контактов
    results = user_db.fetchall('SELECT contact FROM authorized_contacts ORDER BY added_at')
    return [row[0] for row in results]
import sqlite3
from datetime import datetime
from typing import List, Optional
from config import ChannelConfig

class Database:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self):
        """Создание таблиц БД при инициализации"""
        with self.conn:
            # Таблица для хранения настроек каналов
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id INTEGER PRIMARY KEY,
                    posts_per_day INTEGER NOT NULL,
                    start_date TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    last_repost_date TEXT NOT NULL
                )
            ''')

            # Таблица для отслеживания пересланных сообщений
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS reposted_messages (
                    message_id INTEGER,
                    channel_id INTEGER,
                    repost_date TEXT NOT NULL,
                    PRIMARY KEY (message_id, channel_id)
                )
            ''')

    def add_channel(self, config: ChannelConfig):
        """Добавление или обновление канала в БД"""
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO channels 
                VALUES (?, ?, ?, ?, ?)
            ''', (
                config.channel_id,
                config.posts_per_day,
                config.start_date.isoformat(),
                config.is_active,
                config.last_repost_date.isoformat()
            ))

    def get_all_channels(self) -> List[ChannelConfig]:
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM channels')
            return [
                ChannelConfig(
                    channel_id=row[0],
                    posts_per_day=row[1],
                    start_date=datetime.fromisoformat(row[2]),
                    is_active=bool(row[3]),
                    last_repost_date=datetime.fromisoformat(row[4])
                ) 
                for row in cursor.fetchall()
            ]

    def get_channel(self, channel_id: int) -> Optional[ChannelConfig]:
        """Получение конкретного канала по ID"""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM channels WHERE channel_id = ?', (channel_id,))
            row = cursor.fetchone()
            if row:
                return ChannelConfig(
                    channel_id=row[0],
                    posts_per_day=row[1],
                    start_date=datetime.fromisoformat(row[2]),
                    is_active=bool(row[3]),
                    last_repost_date=datetime.fromisoformat(row[4])
                )
            return None

    def update_last_repost(self, channel_id: int, date: datetime):
        """Обновление времени последнего репоста"""
        with self.conn:
            self.conn.execute('''
                UPDATE channels 
                SET last_repost_date = ?
                WHERE channel_id = ?
            ''', (date.isoformat(), channel_id))

    def mark_reposted(self, message_id: int, channel_id: int):
        """Пометить сообщение как пересланное"""
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO reposted_messages 
                VALUES (?, ?, ?)
            ''', (
                message_id,
                channel_id,
                datetime.now().isoformat()
            ))

    def is_reposted(self, message_id: int, channel_id: int) -> bool:
        """Проверить, было ли сообщение переслано"""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT 1 FROM reposted_messages 
                WHERE message_id = ? AND channel_id = ?
            ''', (message_id, channel_id))
            return cursor.fetchone() is not None

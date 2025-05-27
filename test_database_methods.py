import unittest
from database import Database
from config import ChannelConfig
from datetime import datetime

class TestDatabaseMethods(unittest.TestCase):
    def setUp(self):
        # Используем in-memory SQLite для теста
        self.db = Database(':memory:')
        self.config = ChannelConfig(
            channel_id=123,
            posts_per_day=2,
            start_date=datetime.now(),
            is_active=True,
            last_repost_date=datetime.now()
        )
        self.db.add_channel(self.config)

    def test_get_all_channels_exists_and_works(self):
        # Проверяем, что метод существует
        self.assertTrue(hasattr(self.db, 'get_all_channels'))
        # Проверяем, что метод возвращает список ChannelConfig
        channels = self.db.get_all_channels()
        self.assertIsInstance(channels, list)
        self.assertTrue(any(c.channel_id == 123 for c in channels))

if __name__ == '__main__':
    unittest.main()

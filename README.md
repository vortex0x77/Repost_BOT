# Telegram Channel Reposter

Автоматический репостер сообщений для Telegram каналов с возможностью настройки расписания и различными режимами репоста.

## Возможности

- ✨ Автоматический репост сообщений с настраиваемой частотой
- 📅 Планировщик репостов с учетом количества постов в день
- 🔄 Поддержка медленного репоста с настраиваемыми интервалами
- 📚 Репост истории сообщений
- 🗃️ Хранение настроек в SQLite базе данных
- 🔒 Защита от флуда с автоматической обработкой ограничений

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/telegram-channel-reposter.git
cd telegram-channel-reposter
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `config.py` и заполните необходимые данные:
```python
API_ID = "ваш_api_id"
API_HASH = "ваш_api_hash"
SESSION_NAME = "имя_сессии"
DATABASE_NAME = "channels.db"
```

## Использование

1. Запустите бота:
```bash
python main.py
```

2. Доступные команды:
- `/start` - Показать список команд
- `/add_channel <ID>` - Добавить канал
- `/set_limit <ID> <N>` - Установить N постов/день
- `/repost_history <from> <to> [limit=10]` - Репост истории
- `/repost_history_slow <from> <to> <YYYY-MM-DD> <interval_seconds> [limit]` - Медленный репост истории

## Примеры использования

### Добавление канала:
```
/add_channel -1001234567890
```

### Установка лимита постов:
```
/set_limit -1001234567890 5
```

### Медленный репост истории:
```
/repost_history_slow -1001234567890 -1001234567891 2024-01-01 3600 10
```

## Требования

- Python 3.7+
- Telethon
- SQLite3

## Лицензия

MIT License - см. файл [LICENSE](LICENSE)
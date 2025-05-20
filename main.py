import asyncio
import logging
from datetime import datetime, timezone
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from config import API_ID, API_HASH, SESSION_NAME, DATABASE_NAME, ChannelConfig
from database import Database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ChannelReposter:
    def __init__(self):
        self.db = Database(DATABASE_NAME)
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    async def start(self):
        await self.client.start()
        logger.info("Успешная авторизация через MTProto")
        self._register_handlers()
        asyncio.create_task(self._scheduler())
        await self.client.run_until_disconnected()

    def _register_handlers(self):
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await event.reply(
                "📢 Репостер каналов\n\n"
                "Команды:\n"
                "/add_channel <ID> - Добавить канал\n"
                "/set_limit <ID> <N> - Установить N постов/день\n"
                "/repost_history <from> <to> [limit=10] - Репост истории\n"
                "/repost_history_slow <from> <to> <start_date:YYYY-MM-DD> <interval_seconds> [limit] - Медленный репост истории"
            )

        @self.client.on(events.NewMessage(pattern='/add_channel'))
        async def add_channel_handler(event):
            try:
                parts = event.text.split()
                if len(parts) < 2:
                    await event.reply("❌ Формат: /add_channel <ID>")
                    return
                channel_id = int(parts[1])
                if await self._validate_channel(channel_id):
                    config = ChannelConfig(
                        channel_id=channel_id,
                        posts_per_day=5,
                        start_date=datetime.now(),
                        last_repost_date=datetime.now()
                    )
                    self.db.add_channel(config)
                    await event.reply(f"✅ Канал {channel_id} добавлен")
                else:
                    await event.reply(f"❌ Канал {channel_id} не найден или нет доступа")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/set_limit'))
        async def set_limit_handler(event):
            try:
                parts = event.text.split()
                if len(parts) < 3:
                    await event.reply("❌ Формат: /set_limit <ID> <N>")
                    return
                channel_id = int(parts[1])
                new_limit = int(parts[2])
                config = self.db.get_channel(channel_id)
                if not config:
                    await event.reply(f"❌ Канал {channel_id} не найден")
                    return
                config.posts_per_day = new_limit
                self.db.add_channel(config)
                await event.reply(f"✅ Лимит для канала {channel_id} установлен: {new_limit} постов/день")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/repost_history'))
        async def repost_history_handler(event):
            try:
                parts = event.text.split()
                if len(parts) < 3:
                    await event.reply("❌ Формат: /repost_history <from> <to> [limit=10]")
                    return
                source = int(parts[1])
                target = int(parts[2])
                limit = int(parts[3]) if len(parts) > 3 else 10
                count = await self.repost_history(source, target, limit)
                await event.reply(f"✅ Переслано {count} сообщений из {source} в {target}")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/repost_history_slow'))
        async def repost_history_slow_handler(event):
            """Обработчик команды медленного репоста истории"""
            try:
                # Разбиваем команду на части
                command = event.text.strip()
                parts = command.split()
                
                # Проверяем количество аргументов
                if len(parts) < 5:
                    await event.reply(
                        "❌ Неверный формат команды!\n\n"
                        "Правильный формат:\n"
                        "/repost_history_slow <from_id> <to_id> <YYYY-MM-DD> <interval> [limit]\n\n"
                        "Пример:\n"
                        "/repost_history_slow -1002213645726 -1002213645726 2024-01-01 3600 10"
                    )
                    return

                # Парсим ID каналов (должны быть целыми числами)
                try:
                    source_id = int(parts[1])
                    target_id = int(parts[2])
                except ValueError:
                    await event.reply("❌ ID каналов должны быть числами!")
                    return

                # Парсим дату (должна быть в формате YYYY-MM-DD)
                try:
                    date_str = parts[3]
                    if len(date_str) != 10 or date_str.count('-') != 2:
                        raise ValueError("Неверный формат даты")
                    start_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except ValueError:
                    await event.reply(
                        "❌ Неверный формат даты!\n"
                        "Используйте формат YYYY-MM-DD, например: 2024-01-01"
                    )
                    return

                # Парсим интервал (должен быть положительным числом)
                try:
                    interval = int(parts[4])
                    if interval <= 0:
                        raise ValueError("Интервал должен быть положительным")
                except ValueError:
                    await event.reply(
                        "❌ Интервал должен быть положительным числом секунд!\n"
                        "Например: 3600 для одного часа"
                    )
                    return

                # Парсим лимит (опционально)
                limit = 1000  # значение по умолчанию
                if len(parts) > 5:
                    try:
                        limit = int(parts[5])
                        if limit <= 0:
                            raise ValueError("Лимит должен быть положительным")
                    except ValueError:
                        await event.reply("❌ Лимит должен быть положительным числом!")
                        return

                # Запускаем медленный репост
                await event.reply(
                    f"✅ Начинаю медленный репост...\n"
                    f"- Из канала: {source_id}\n"
                    f"- В канал: {target_id}\n"
                    f"- Начиная с даты: {start_date.strftime('%Y-%m-%d')}\n"
                    f"- Интервал: {interval} сек.\n"
                    f"- Максимум сообщений: {limit}"
                )

                count = await self.repost_history_slow(source_id, target_id, start_date, interval, limit)
                
                await event.reply(
                    f"✅ Репост завершён!\n"
                    f"Переслано {count} сообщений"
                )

            except Exception as e:
                logger.error(f"Ошибка в repost_history_slow: {str(e)}")
                await event.reply(f"❌ Произошла ошибка: {str(e)}")
                return

    async def _validate_channel(self, channel_id: int) -> bool:
        try:
            entity = await self.client.get_entity(channel_id)
            return hasattr(entity, 'title')
        except Exception as e:
            logger.error(f"Ошибка валидации: {str(e)}")
            return False

    async def _scheduler(self):
        while True:
            try:
                await self._process_channels()
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Ошибка планировщика: {str(e)}")

    async def _process_channels(self):
        try:
            channels = self.db.get_all_channels()
            for config in channels:
                if config.is_active:
                    await self._process_channel(config)
        except Exception as e:
            logger.error(f"Ошибка обработки каналов: {str(e)}")

    async def _process_channel(self, config: ChannelConfig):
        try:
            time_diff = datetime.now() - config.last_repost_date
            posts_needed = int((time_diff.total_seconds() / 86400) * config.posts_per_day)
            if posts_needed < 1:
                return

            channel = await self.client.get_entity(config.channel_id)
            messages = await self.client.get_messages(
                channel,
                limit=min(posts_needed, 100),
                offset_date=datetime.now()
            )

            # Фильтруем только обычные сообщения (не MessageService)
            filtered_messages = [msg for msg in reversed(messages) if not msg.action]

            for msg in filtered_messages:
                try:
                    await self.client.forward_messages(channel, msg)
                    self.db.update_last_repost(config.channel_id, datetime.now())
                    await asyncio.sleep(86400 / config.posts_per_day)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    logger.error(f"Ошибка репоста: {str(e)}")

        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logger.error(f"Ошибка канала {config.channel_id}: {str(e)}")

    async def repost_history(self, source: int, target: int, limit: int = 10):
        try:
            src = await self.client.get_entity(source)
            dst = await self.client.get_entity(target)
            messages = []
            async for msg in self.client.iter_messages(src, limit=limit):
                # Фильтруем только обычные сообщения (не MessageService)
                if not msg.action:
                    messages.append(msg)
                await asyncio.sleep(0.5)
            for msg in reversed(messages):
                await self.client.forward_messages(dst, msg)
                await asyncio.sleep(1)
            return len(messages)
        except Exception as e:
            logger.error(f"Ошибка истории: {str(e)}")
            raise

    async def repost_history_slow(self, source: int, target: int, start_date: datetime, interval: int, limit: int = 1000):
        try:
            src = await self.client.get_entity(source)
            dst = await self.client.get_entity(target)
            messages = []
            # Собираем сообщения начиная с start_date (по возрастанию даты)
            async for msg in self.client.iter_messages(src, offset_date=start_date, reverse=True):
                if not msg.action and msg.date >= start_date:
                    messages.append(msg)
                    if len(messages) >= limit:
                        break
            sent = 0
            for msg in messages:
                await self.client.forward_messages(dst, msg)
                sent += 1
                await asyncio.sleep(interval)
            return sent
        except Exception as e:
            logger.error(f"Ошибка медленного репоста: {str(e)}")
            raise

async def main():
    reposter = ChannelReposter()
    await reposter.start()

if __name__ == '__main__':
    asyncio.run(main())

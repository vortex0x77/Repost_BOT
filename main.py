import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, ChannelPrivateError
from telethon.tl.types import Message
from config import API_ID, API_HASH, SESSION_NAME, DATABASE_NAME, ChannelConfig
from database import Database

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def ensure_utc(dt: datetime) -> datetime:
    """Гарантирует, что datetime aware и в UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

class ChannelReposter:
    def __init__(self):
        self.db = Database(DATABASE_NAME)
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.active_tasks: Dict[int, asyncio.Task] = {}

    async def start(self):
        await self.client.start()
        logger.info("Бот успешно запущен")
        self._register_handlers()
        await self._restart_active_channels()
        await self.client.run_until_disconnected()

    async def _restart_active_channels(self):
        channels = self.db.get_all_channels()
        for config in channels:
            if config.is_active:
                logger.info(f"Перезапуск канала {config.channel_id}")
                self._start_channel_task(config)

    def _start_channel_task(self, config: ChannelConfig):
        if config.channel_id in self.active_tasks:
            self.active_tasks[config.channel_id].cancel()
        self.active_tasks[config.channel_id] = asyncio.create_task(
            self._channel_worker(config)
        )

    async def _channel_worker(self, config: ChannelConfig):
        logger.info(f"Запуск воркера для канала {config.channel_id}")
        while config.is_active:
            try:
                config = self.db.get_channel(config.channel_id)
                if not config or not config.is_active:
                    break
                await self._process_channel(config)
                await asyncio.sleep(300)
            except FloodWaitError as e:
                logger.warning(f"Flood wait на {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Ошибка воркера канала: {str(e)}")
                await asyncio.sleep(60)
        logger.info(f"Воркер остановлен для канала {config.channel_id}")

    async def _process_channel(self, config: ChannelConfig):
        now = datetime.now(timezone.utc)
        start_date = ensure_utc(config.start_date)
        last_repost_date = ensure_utc(config.last_repost_date)
        if now < start_date:
            logger.info(f"Канал {config.channel_id} ещё не начал работу")
            return
        time_diff = now - last_repost_date
        posts_needed = int((time_diff.total_seconds() / 86400) * config.posts_per_day)
        if posts_needed < 1:
            return
        logger.info(f"Обработка канала {config.channel_id}, требуется {posts_needed} постов")
        try:
            channel = await self._get_entity(config.channel_id)
            messages = await self._fetch_messages(channel, last_repost_date, posts_needed)
            if not messages:
                logger.info(f"Нет новых сообщений в канале {config.channel_id}")
                return
            grouped_messages = self._group_messages(messages)
            sent_count = 0
            for message_group in grouped_messages:
                if sent_count >= posts_needed:
                    break
                if await self._forward_messages(channel, message_group):
                    sent_count += 1
                    self.db.update_last_repost(config.channel_id, now)
                    delay = getattr(config, 'interval_seconds', None) or (86400 / config.posts_per_day)
                    await asyncio.sleep(delay)
            logger.info(f"Отправлено {sent_count} сообщений из канала {config.channel_id}")
        except ChannelPrivateError:
            logger.error(f"Канал {config.channel_id} приватный или недоступен")
            config.is_active = False
            self.db.add_channel(config)
        except Exception as e:
            logger.error(f"Ошибка обработки канала {config.channel_id}: {str(e)}")

    async def _get_entity(self, channel_id: int):
        try:
            return await self.client.get_entity(channel_id)
        except Exception as e:
            logger.error(f"Ошибка получения entity {channel_id}: {str(e)}")
            raise

    async def _fetch_messages(self, channel, offset_date: datetime, limit: int) -> List[Message]:
        try:
            offset_date = ensure_utc(offset_date)
            return await self.client.get_messages(
                channel,
                limit=min(limit * 3, 100),
                offset_date=offset_date
            )
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {str(e)}")
            return []

    def _group_messages(self, messages: List[Message]) -> List[List[Message]]:
        albums = []
        single_messages = []
        grouped = {}
        for msg in reversed(messages):
            if not msg:
                continue
            if getattr(msg, 'grouped_id', None):
                grouped.setdefault(msg.grouped_id, []).append(msg)
            else:
                single_messages.append(msg)
        for group in sorted(grouped.values(), key=lambda x: x[0].date):
            albums.append(sorted(group, key=lambda m: m.id))
        return albums + [[msg] for msg in single_messages]

    async def _forward_messages(self, target_channel, messages: List[Message]) -> bool:
        if not messages or not any(messages):
            return False
        try:
            send_as = await self._get_send_as_entity(target_channel)
            first_msg = messages[0]
            if len(messages) == 1:
                return await self._send_single_message(target_channel, first_msg, send_as)
            return await self._send_album(target_channel, messages, send_as)
        except Exception as e:
            logger.error(f"Ошибка пересылки сообщений: {str(e)}")
            return False

    async def _get_send_as_entity(self, channel):
        try:
            return await self.client.get_entity(channel)
        except Exception as e:
            logger.warning(f"Не удалось получить send_as entity: {str(e)}")
            return None

    async def _send_single_message(self, target_channel, message: Message, send_as) -> bool:
        has_content = bool(message.text or message.media)
        if not has_content:
            logger.warning("Пропущено пустое сообщение")
            return False
        try:
            await self.client.send_message(
                entity=target_channel,
                message=message.text or "",
                file=message.media,
                link_preview=bool(getattr(message, 'web_preview', False)),
                buttons=getattr(message, 'buttons', None),
                send_as=send_as
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки одиночного сообщения: {str(e)}")
            return False

    async def _send_album(self, target_channel, messages: List[Message], send_as) -> bool:
        media = []
        captions = []
        for msg in messages:
            if msg and msg.media:
                media.append(msg.media)
                captions.append(msg.text or "")
        if not media:
            logger.warning("В альбоме нет медиа")
            return False
        try:
            await self.client.send_file(
                entity=target_channel,
                file=media,
                caption=captions[0] if captions else "",
                send_as=send_as
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки альбома: {str(e)}")
            return False

    def _register_handlers(self):
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            help_text = (
                "📢 Бот репостер каналов\n\n"
                "Команды:\n"
                "/add_channel <ID> [ГГГГ-ММ-ДД] [постов/день] [интервал_сек] - Добавить канал\n"
                "/set_limit <ID> <N> - Установить лимит постов в день\n"
                "/start_channel <ID> - Запустить постинг\n"
                "/stop_channel <ID> - Остановить постинг\n"
                "/channel_info <ID> - Показать настройки канала\n"
                "/repost_history <откуда> <куда> [лимит] - Быстрый репост\n"
                "/repost_history_slow <откуда> <куда> <дата> <интервал> [лимит] - Медленный репост"
            )
            await event.reply(help_text)

        @self.client.on(events.NewMessage(pattern='/add_channel'))
        async def add_channel_handler(event):
            try:
                args = event.text.split()
                if len(args) < 2:
                    return await event.reply("❌ Формат: /add_channel <ID> [дата] [лимит] [интервал]")
                channel_id = int(args[1])
                if not await self._validate_channel(channel_id):
                    return await event.reply("❌ Канал не найден или нет доступа")
                params = self._parse_channel_params(args[2:])
                config = ChannelConfig(
                    channel_id=channel_id,
                    posts_per_day=params['limit'],
                    start_date=ensure_utc(params['date']),
                    last_repost_date=datetime.now(timezone.utc),
                    is_active=True,
                    interval_seconds=params['interval']
                )
                self.db.add_channel(config)
                self._start_channel_task(config)
                response = (
                    f"✅ Канал добавлен:\n"
                    f"ID: {channel_id}\n"
                    f"Старт: {params['date'].strftime('%Y-%m-%d')}\n"
                    f"Постов/день: {params['limit']}\n"
                    f"Интервал: {params['interval'] or 'авто'} сек"
                )
                await event.reply(response)
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/set_limit'))
        async def set_limit_handler(event):
            try:
                args = event.text.split()
                if len(args) < 3:
                    return await event.reply("❌ Формат: /set_limit <ID> <постов_в_день>")
                channel_id = int(args[1])
                posts_per_day = int(args[2])
                config = self.db.get_channel(channel_id)
                if not config:
                    return await event.reply("❌ Канал не найден")
                config.posts_per_day = posts_per_day
                self.db.add_channel(config)
                await event.reply(f"✅ Для канала {channel_id} установлен лимит {posts_per_day} постов/день")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/channel_info'))
        async def channel_info_handler(event):
            try:
                args = event.text.split()
                if len(args) < 2:
                    return await event.reply("❌ Формат: /channel_info <ID>")
                channel_id = int(args[1])
                config = self.db.get_channel(channel_id)
                if not config:
                    return await event.reply("❌ Канал не найден")
                info = (
                    f"ℹ️ Информация о канале:\n"
                    f"ID: {config.channel_id}\n"
                    f"Активен: {'Да' if config.is_active else 'Нет'}\n"
                    f"Дата старта: {config.start_date.strftime('%Y-%m-%d')}\n"
                    f"Постов/день: {config.posts_per_day}\n"
                    f"Интервал: {config.interval_seconds or 'авто'} сек\n"
                    f"Последний репост: {config.last_repost_date.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await event.reply(info)
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/repost_history '))
        async def repost_history_handler(event):
            try:
                args = event.text.split()
                if len(args) < 3:
                    return await event.reply("❌ Формат: /repost_history <откуда> <куда> [лимит]")
                from_channel = int(args[1])
                to_channel = int(args[2])
                limit = int(args[3]) if len(args) > 3 else 10
                await self._fast_repost(from_channel, to_channel, limit, event)
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/repost_history_slow'))
        async def repost_history_slow_handler(event):
            try:
                args = event.text.split()
                if len(args) < 5:
                    return await event.reply("❌ Формат: /repost_history_slow <откуда> <куда> <дата> <интервал> [лимит]")
                from_channel = int(args[1])
                to_channel = int(args[2])
                date = ensure_utc(datetime.strptime(args[3], "%Y-%m-%d"))
                interval = int(args[4])
                limit = int(args[5]) if len(args) > 5 else 10
                await self._slow_repost(from_channel, to_channel, date, interval, limit, event)
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/start_channel'))
        async def start_channel_handler(event):
            try:
                channel_id = int(event.text.split()[1])
                config = self.db.get_channel(channel_id)
                if not config:
                    return await event.reply("❌ Канал не найден")
                config.is_active = True
                self.db.add_channel(config)
                self._start_channel_task(config)
                await event.reply(f"✅ Канал {channel_id} запущен")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

        @self.client.on(events.NewMessage(pattern='/stop_channel'))
        async def stop_channel_handler(event):
            try:
                channel_id = int(event.text.split()[1])
                config = self.db.get_channel(channel_id)
                if not config:
                    return await event.reply("❌ Канал не найден")
                config.is_active = False
                self.db.add_channel(config)
                if channel_id in self.active_tasks:
                    self.active_tasks[channel_id].cancel()
                    del self.active_tasks[channel_id]
                await event.reply(f"⏸ Канал {channel_id} остановлен")
            except Exception as e:
                await event.reply(f"❌ Ошибка: {str(e)}")

    def _parse_channel_params(self, args: List[str]) -> Dict:
        params = {
            'date': datetime.now(timezone.utc),
            'limit': 5,
            'interval': None
        }
        if not args:
            return params
        try:
            naive_date = datetime.strptime(args[0], "%Y-%m-%d")
            params['date'] = naive_date.replace(tzinfo=timezone.utc)
            args = args[1:]
        except (ValueError, IndexError):
            pass
        if args:
            try:
                params['limit'] = max(1, int(args[0]))
                args = args[1:]
            except (ValueError, IndexError):
                pass
        if args:
            try:
                params['interval'] = max(1, int(args[0]))
            except (ValueError, IndexError):
                pass
        return params

    async def _validate_channel(self, channel_id: int) -> bool:
        try:
            entity = await self.client.get_entity(channel_id)
            return hasattr(entity, 'title')
        except Exception as e:
            logger.error(f"Ошибка валидации: {str(e)}")
            return False

    async def _fast_repost(self, from_channel: int, to_channel: int, limit: int, event):
        try:
            from_entity = await self._get_entity(from_channel)
            to_entity = await self._get_entity(to_channel)
            messages = await self.client.get_messages(from_entity, limit=limit)
            count = 0
            for msg in reversed(messages):
                if not msg or (not msg.text and not msg.media):
                    continue
                await self.client.send_message(
                    entity=to_entity,
                    message=msg.text or "",
                    file=msg.media,
                    link_preview=bool(getattr(msg, 'web_preview', False)),
                    buttons=getattr(msg, 'buttons', None)
                )
                count += 1
                await asyncio.sleep(1)
            await event.reply(f"✅ Быстро переслано {count} сообщений из {from_channel} в {to_channel}")
        except Exception as e:
            await event.reply(f"❌ Ошибка при быстром репосте: {str(e)}")

    async def _slow_repost(self, from_channel: int, to_channel: int, date: datetime, interval: int, limit: int, event):
        try:
            from_entity = await self._get_entity(from_channel)
            to_entity = await self._get_entity(to_channel)
            messages = await self.client.get_messages(from_entity, limit=limit, offset_date=date)
            count = 0
            for msg in reversed(messages):
                if not msg or (not msg.text and not msg.media):
                    continue
                await self.client.send_message(
                    entity=to_entity,
                    message=msg.text or "",
                    file=msg.media,
                    link_preview=bool(getattr(msg, 'web_preview', False)),
                    buttons=getattr(msg, 'buttons', None)
                )
                count += 1
                await asyncio.sleep(interval)
            await event.reply(f"✅ Медленно переслано {count} сообщений из {from_channel} в {to_channel} с интервалом {interval} сек")
        except Exception as e:
            await event.reply(f"❌ Ошибка при медленном репосте: {str(e)}")

async def main():
    reposter = ChannelReposter()
    await reposter.start()

if __name__ == '__main__':
    asyncio.run(main())
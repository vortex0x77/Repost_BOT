from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChannelConfig:
    channel_id: int
    posts_per_day: int
    start_date: datetime
    is_active: bool = True
    last_repost_date: datetime = datetime.now()

# Telegram API credentials
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
SESSION_NAME = "YOUR_SESSION_NAME"
DATABASE_NAME = "channels.db"
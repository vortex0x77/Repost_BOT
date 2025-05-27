from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class ChannelConfig:
    channel_id: int
    posts_per_day: int
    start_date: datetime
    is_active: bool = True
    last_repost_date: datetime = field(default_factory=lambda: datetime.now())
    interval_seconds: Optional[int] = None

API_ID = 20871122
API_HASH = "1f25ee7d62859a93eb9d3eeec9375ccc"
SESSION_NAME = "Skuff"
DATABASE_NAME = "channels.db"
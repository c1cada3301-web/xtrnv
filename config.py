import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS: list[int] = [
        int(x.strip())
        for x in os.getenv("ADMIN_IDS", "").split(",")
        if x.strip().isdigit()
    ]
    MTPROXY_SCRIPT: str = os.getenv("MTPROXY_SCRIPT", "/opt/mtproxymax/mtproxymax")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()

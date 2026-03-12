from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from config import config


class AdminMiddleware(BaseMiddleware):
    """Пропускает только пользователей из ADMIN_IDS."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")

        if not user or user.id not in config.ADMIN_IDS:
            if isinstance(event, Message):
                await event.answer("🚫 Нет доступа.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Нет доступа.", show_alert=True)
            return

        return await handler(event, data)

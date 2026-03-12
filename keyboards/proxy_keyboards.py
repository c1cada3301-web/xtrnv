from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_driver_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="💎 Прокси"), KeyboardButton(text="🔑 Секреты"))
    builder.row(KeyboardButton(text="📊 Статистика"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие...")

def get_back_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⬅️ Назад"))
    return builder.as_markup(resize_keyboard=True)

def get_confirm_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
                InlineKeyboardButton(text="🚫 Отмена", callback_data="back")
            ]
        ]
    )

def get_actions_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Все секреты", callback_data="all_secrets")],
            [InlineKeyboardButton(text="📎 Ссылка по имени", callback_data="get_link")],
            [InlineKeyboardButton(text="👤 Добавить пользователя", callback_data="add_user")],
            [InlineKeyboardButton(text="🚫 Удалить пользователя", callback_data="remove_user")],
            [InlineKeyboardButton(text="⭕️ Сменить секрет", callback_data="edit_secret")],
            [InlineKeyboardButton(text="🔄 Перезапустить прокси", callback_data="restart_proxy")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
    )
from aiogram.fsm.state import StatesGroup, State


class MTProxyStates(StatesGroup):
    waiting_label_add = State()     # ввод имени при добавлении пользователя
    waiting_label_remove = State()  # ввод имени при удалении
    waiting_label_rotate = State()  # ввод имени при смене секрета
    waiting_label_link = State()    # ввод имени для получения ссылки

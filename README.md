# MTProxy Bot

Telegram-бот для управления секретами [MTProxyMax](https://github.com/SamNet-dev/MTProxyMax) через удобный интерфейс вместо bash-скрипта.

## Возможности

- Просмотр статуса прокси и списка пользователей
- Добавление / удаление пользователей
- Смена секрета (rotate)
- Получение ссылки подключения + QR-код
- Перезапуск прокси
- Доступ только для указанных администраторов

## Структура проекта

```
├── main.py                  # точка входа
├── config.py                # конфигурация
├── services/
│   └── mtproxy.py           # обёртка над /opt/mtproxymax/mtproxymax
├── handlers/
│   └── mtproxy.py           # все хендлеры
├── states/
│   └── states.py            # FSM-состояния
├── middlewares/
│   └── auth.py              # AdminMiddleware
├── keyboards/
│   └── proxy_keyboards.py   # клавиатуры
└── utils/
    └── qr.py                # генерация QR-кодов
```

## Установка

```bash
git clone <repo>
cd xtrnv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Создай файл `.env`:

```env
BOT_TOKEN=токен_от_BotFather
ADMIN_IDS=123456789,987654321
MTPROXY_SCRIPT=/opt/mtproxymax/mtproxymax
```

| Переменная       | Описание                                              |
|------------------|-------------------------------------------------------|
| `BOT_TOKEN`      | Токен бота от [@BotFather](https://t.me/BotFather)   |
| `ADMIN_IDS`      | Telegram ID администраторов через запятую             |
| `MTPROXY_SCRIPT` | Путь к скрипту mtproxymax (по умолчанию как выше)     |

## Запуск

```bash
python main.py
```

## Использование

| Кнопка           | Действие                                         |
|------------------|--------------------------------------------------|
| 💎 Прокси        | Статус прокси-сервера                            |
| 🔑 Секреты       | Меню управления пользователями                   |
| 🛠 Подключение   | Ссылка подключения + QR-код для пользователя     |
| 📊 Статистика    | Список всех пользователей                        |

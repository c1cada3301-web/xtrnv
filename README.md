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

## Деплой на сервер (systemd)

> **Важно:** этот бот заменяет встроенный bash-бот MTProxyMax (`mtproxymax-telegram.sh`).
> Перед установкой его нужно остановить и отключить из автозапуска, иначе два бота
> будут конфликтовать за один Telegram-токен.

```bash
# 0. Отключить старый bash-бот MTProxyMax
systemctl stop mtproxymax-telegram 2>/dev/null
systemctl disable mtproxymax-telegram 2>/dev/null
pkill -f mtproxymax-telegram.sh 2>/dev/null

# 1. Скопировать проект
git clone <repo> /opt/mtproxy-bot
cd /opt/mtproxy-bot

# 2. Создать venv и установить зависимости
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Создать .env (см. раздел «Настройка»)
nano .env

# 4. Установить systemd-сервис
cp mtproxy-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mtproxy-bot
systemctl start mtproxy-bot
```

Управление:
```bash
systemctl status mtproxy-bot   # статус
journalctl -u mtproxy-bot -f   # логи в реальном времени
systemctl restart mtproxy-bot  # перезапуск
systemctl stop mtproxy-bot     # остановка
```

## Локальный запуск

```bash
python main.py
```

## Использование

| Кнопка           | Действие                                                        |
|------------------|-----------------------------------------------------------------|
| 💎 Прокси        | Общий статус: uptime, порт, трафик суммарно, кол-во соединений  |
| 📊 Статистика    | Таблица по каждому секрету: трафик, статус, дата создания       |
| 🔑 Секреты       | Управление пользователями (добавить/удалить/ротация/ссылки)     |

**Меню «Секреты»:**

| Кнопка                | Действие                                          |
|-----------------------|---------------------------------------------------|
| 🔗 Все секреты        | Список всех пользователей с tg:// ссылками        |
| 📎 Ссылка по имени    | Ссылка + QR-код для конкретного пользователя      |
| 👤 Добавить           | Создать нового пользователя                       |
| 🚫 Удалить            | Удалить пользователя                              |
| ⭕️ Сменить секрет     | Ротация ключа пользователя                        |
| 🔄 Перезапустить      | Перезапустить прокси-сервер                       |

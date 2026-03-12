import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from config import config
from states.states import MTProxyStates
from services import mtproxy as mp
from keyboards.proxy_keyboards import (
    get_driver_main_menu,
    get_back_keyboard,
    get_actions_menu_inline,
    get_confirm_inline_keyboard,
)
from utils.qr import extract_proxy_link, make_qr_bytes

logger = logging.getLogger(__name__)
router = Router()


# ─── Главное меню ────────────────────────────────────────────────────────────

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 MTProxy управление\nВыберите раздел:",
        reply_markup=get_driver_main_menu(),
    )


# ─── Кнопка «🔑 Секреты» ─────────────────────────────────────────────────────

@router.message(F.text == "🔑 Секреты")
async def menu_secrets(message: Message):
    await message.answer("Управление пользователями:", reply_markup=get_actions_menu_inline())


# ─── Кнопка «💎 Прокси» ──────────────────────────────────────────────────────

@router.message(F.text == "💎 Прокси")
async def menu_proxy(message: Message):
    ok, out = await mp.secret_list()
    if not ok:
        await message.answer(f"❌ Ошибка: {out}")
        return

    lines = ["💎 <b>Трафик по секретам</b>\n"]
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        # формат: N  label  ●  active  date  traffic_in  unit_in  traffic_out  unit_out
        name = parts[1]
        # трафик in/out — берём последние 4 токена (val unit val unit)
        try:
            t_in = f"{parts[-4]} {parts[-3]}"
            t_out = f"{parts[-2]} {parts[-1]}"
        except IndexError:
            t_in = t_out = "—"
        lines.append(f"<tg-emoji emoji-id='5343939876100262740'>🟢</tg-emoji><b>{name}</b>  ↓{t_in}  ↑{t_out}\n\n")

    await message.answer("\n".join(lines), parse_mode="HTML")


# ─── Кнопка «📊 Статистика» ───────────────────────────────────────────────────

@router.message(F.text == "📊 Статистика")
async def menu_stats(message: Message):
    ok, out = await mp.proxy_status()

    import re
    def _get(pattern, default="—"):
        m = re.search(pattern, out)
        return m.group(1).strip() if m else default

    status_word = _get(r"Status:\s+\S+\s+(\w+)")
    status_icon = "🟢" if "RUNNING" in out.upper() else "🔴"
    engine   = _get(r"Engine:\s+(\S+)")
    port     = _get(r"Port:\s+(\S+)")
    uptime   = _get(r"Uptime:\s+(\S+)")
    domain   = _get(r"Domain:\s+(\S+)")
    traffic  = _get(r"Traffic:\s+(↓[^\n]+?)(?:\s{2,}|\n)")
    conns    = _get(r"Connections:\s+(\d+)")
    secrets  = _get(r"Secrets:\s+([^\n]+)")

    text = (
        f"{status_icon} <b>Статус прокси</b>\n\n"
        f"Статус: <b>{status_word}</b>\n"
        f"Engine: {engine}\n"
        f"Порт: {port}\n"
        f"Домен: {domain}\n"
        f"Аптайм: {uptime}\n"
        f"Трафик: {traffic}\n"
        f"Соединений: {conns}\n"
        f"Секреты: {secrets}"
    )
    await message.answer(text, parse_mode="HTML")


# ─── Inline: ссылка по имени (+ QR) ─────────────────────────────────────────

@router.callback_query(F.data == "get_link")
async def cb_get_link(callback: CallbackQuery, state: FSMContext):
    _, users = await mp.secret_list()
    await callback.message.answer(
        f"<b>Текущие пользователи:</b>\n<pre>{users}</pre>\n\nВведите имя пользователя для получения ссылки:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(MTProxyStates.waiting_label_link)
    await callback.answer()


# ─── Inline: список всех секретов со ссылками ────────────────────────────────

@router.callback_query(F.data == "all_secrets")
async def cb_all_secrets(callback: CallbackQuery):
    ok, out = await mp.secret_list()
    if not ok:
        await callback.message.answer(f"❌ Ошибка: {out}")
        await callback.answer()
        return

    lines = []
    for line in out.splitlines():
        parts = line.strip().split()
        # формат строки: "N  label  ● active ..."
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        name = parts[1]
        lok, lout = await mp.secret_link(name)
        link = extract_proxy_link(lout) if lok else None
        if link:
            lines.append(f"<b>🗽{name}</b>\n<code>{link}</code>")
        else:
            lines.append(f"<b>{name}</b> — ссылка недоступна")

    text = "\n\n".join(lines) if lines else "Пользователей нет"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# ─── Inline: добавить пользователя ───────────────────────────────────────────

@router.callback_query(F.data == "add_user")
async def cb_add_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите имя нового пользователя (латиница, без пробелов):",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(MTProxyStates.waiting_label_add)
    await callback.answer()


@router.message(MTProxyStates.waiting_label_add)
async def process_label_add(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Отмена.", reply_markup=get_driver_main_menu())
        return

    label = message.text.strip()
    if not label.isascii() or " " in label:
        await message.answer("Имя должно быть на латинице без пробелов. Попробуйте ещё раз:")
        return

    await state.update_data(label=label)
    await message.answer(
        f"Добавить пользователя <b>{label}</b>?",
        parse_mode="HTML",
        reply_markup=get_confirm_inline_keyboard(),
    )


@router.callback_query(F.data == "confirm", MTProxyStates.waiting_label_add)
async def cb_confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    label = data.get("label", "")
    await state.clear()

    ok, out = await mp.secret_add(label)
    if ok:
        await callback.message.edit_text(f"✅ Пользователь <b>{label}</b> добавлен\n\n<pre>{out}</pre>", parse_mode="HTML")
    else:
        await callback.message.edit_text(f"❌ Ошибка: <pre>{out}</pre>", parse_mode="HTML")
    await callback.answer()


# ─── Inline: удалить пользователя ────────────────────────────────────────────

@router.callback_query(F.data == "remove_user")
async def cb_remove_user(callback: CallbackQuery, state: FSMContext):
    _, users = await mp.secret_list()
    await callback.message.answer(
        f"<b>Текущие пользователи:</b>\n<pre>{users}</pre>\n\nВведите имя пользователя для удаления:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(MTProxyStates.waiting_label_remove)
    await callback.answer()


@router.message(MTProxyStates.waiting_label_remove)
async def process_label_remove(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Отмена.", reply_markup=get_driver_main_menu())
        return

    label = message.text.strip()
    await state.update_data(label=label)
    await message.answer(
        f"Удалить пользователя <b>{label}</b>? Это действие нельзя отменить.",
        parse_mode="HTML",
        reply_markup=get_confirm_inline_keyboard(),
    )


@router.callback_query(F.data == "confirm", MTProxyStates.waiting_label_remove)
async def cb_confirm_remove(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    label = data.get("label", "")
    await state.clear()

    ok, out = await mp.secret_remove(label)
    if ok:
        await callback.message.edit_text(f"✅ Пользователь <b>{label}</b> удалён", parse_mode="HTML")
    else:
        await callback.message.edit_text(f"❌ Ошибка: <pre>{out}</pre>", parse_mode="HTML")
    await callback.answer()


# ─── Inline: сменить секрет ───────────────────────────────────────────────────

@router.callback_query(F.data == "edit_secret")
async def cb_edit_secret(callback: CallbackQuery, state: FSMContext):
    _, users = await mp.secret_list()
    await callback.message.answer(
        f"<b>Текущие пользователи:</b>\n<pre>{users}</pre>\n\nВведите имя пользователя для смены секрета:",
        parse_mode="HTML",
        reply_markup=get_back_keyboard(),
    )
    await state.set_state(MTProxyStates.waiting_label_rotate)
    await callback.answer()


@router.message(MTProxyStates.waiting_label_rotate)
async def process_label_rotate(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Отмена.", reply_markup=get_driver_main_menu())
        return

    label = message.text.strip()
    await state.update_data(label=label)
    await message.answer(
        f"Сменить секрет для <b>{label}</b>?",
        parse_mode="HTML",
        reply_markup=get_confirm_inline_keyboard(),
    )


@router.callback_query(F.data == "confirm", MTProxyStates.waiting_label_rotate)
async def cb_confirm_rotate(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    label = data.get("label", "")
    await state.clear()

    ok, out = await mp.secret_rotate(label)
    if ok:
        await callback.message.edit_text(
            f"✅ Секрет для <b>{label}</b> обновлён\n\n<pre>{out}</pre>",
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(f"❌ Ошибка: <pre>{out}</pre>", parse_mode="HTML")
    await callback.answer()


# ─── Inline: получить ссылку подключения ─────────────────────────────────────

@router.message(MTProxyStates.waiting_label_link)
async def process_label_link(message: Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Отмена.", reply_markup=get_driver_main_menu())
        return

    label = message.text.strip()
    await state.clear()

    ok, out = await mp.secret_link(label)
    if not ok:
        await message.answer(f"❌ Ошибка: {out}", reply_markup=get_driver_main_menu())
        return

    await message.answer(
        f"🔗 <b>Ссылка для {label}</b>\n\n<pre>{out}</pre>",
        parse_mode="HTML",
        reply_markup=get_driver_main_menu(),
    )

    link = extract_proxy_link(out)
    if link:
        qr_buf = make_qr_bytes(link)
        await message.answer_photo(
            BufferedInputFile(qr_buf.read(), filename="proxy_qr.png"),
            caption=f"📱 QR-код для <b>{label}</b>",
            parse_mode="HTML",
        )


# ─── Inline: перезапуск прокси ───────────────────────────────────────────────

@router.callback_query(F.data == "restart_proxy")
async def cb_restart_proxy(callback: CallbackQuery):
    await callback.message.edit_text("⏳ Перезапускаю прокси...")
    ok, out = await mp.proxy_restart()
    if ok:
        await callback.message.edit_text(f"✅ Прокси перезапущен\n\n<pre>{out}</pre>", parse_mode="HTML")
    else:
        await callback.message.edit_text(f"❌ Ошибка: <pre>{out}</pre>", parse_mode="HTML")
    await callback.answer()


# ─── Inline: отмена ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "back")
async def cb_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer()

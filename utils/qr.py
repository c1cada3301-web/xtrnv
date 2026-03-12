import io
import re
import qrcode
from qrcode.image.pil import PilImage


def extract_proxy_link(output: str) -> str | None:
    """Извлекает tg://proxy?... или https://t.me/proxy?... ссылку из вывода mtproxymax."""
    for pattern in (r"tg://proxy\?[^\s]+", r"https://t\.me/proxy\?[^\s]+"):
        m = re.search(pattern, output)
        if m:
            return m.group(0)
    return None


def make_qr_bytes(data: str) -> io.BytesIO:
    """Генерирует QR-код и возвращает PNG в BytesIO."""
    img: PilImage = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

import re
import asyncio
import logging
from config import config

logger = logging.getLogger(__name__)

SCRIPT = config.MTPROXY_SCRIPT
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


async def _run(*args: str) -> tuple[bool, str]:
    """Запускает команду mtproxymax, возвращает (успех, вывод)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            SCRIPT, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = _strip_ansi(stdout.decode().strip() or stderr.decode().strip())
        success = proc.returncode == 0
        if not success:
            logger.warning("mtproxymax %s exit=%d stderr=%s", args, proc.returncode, stderr.decode().strip())
        return success, output
    except asyncio.TimeoutError:
        logger.error("mtproxymax %s timed out", args)
        return False, "Команда не ответила за 30 секунд"
    except FileNotFoundError:
        return False, f"Скрипт не найден: {SCRIPT}"
    except Exception as e:
        logger.error("mtproxymax error: %s", e)
        return False, str(e)


async def secret_list() -> tuple[bool, str]:
    return await _run("secret", "list")


async def secret_add(label: str) -> tuple[bool, str]:
    return await _run("secret", "add", label)


async def secret_remove(label: str) -> tuple[bool, str]:
    return await _run("secret", "remove", label)


async def secret_rotate(label: str) -> tuple[bool, str]:
    return await _run("secret", "rotate", label)


async def secret_link(label: str) -> tuple[bool, str]:
    return await _run("secret", "link", label)


async def secret_enable(label: str) -> tuple[bool, str]:
    return await _run("secret", "enable", label)


async def secret_disable(label: str) -> tuple[bool, str]:
    return await _run("secret", "disable", label)


async def proxy_restart() -> tuple[bool, str]:
    return await _run("restart")


async def proxy_status() -> tuple[bool, str]:
    return await _run("status")

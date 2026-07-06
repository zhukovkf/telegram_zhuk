#!/usr/bin/env python3
"""
Берёт следующий по очереди пост из queue/, публикует его в Telegram-канал
и переносит файл в published/. Предназначен для запуска из GitHub Actions
по расписанию (см. .github/workflows/publish.yml), но можно запускать и
локально для теста.

Переменные окружения:
    TELEGRAM_BOT_TOKEN — токен бота от @BotFather (хранить в GitHub Secrets,
                         не в коде и не в репозитории)
    TELEGRAM_CHANNEL    — username канала, например @telezhukkk
                         (по умолчанию берётся значение ниже, можно
                         переопределить переменной окружения/GitHub Variables)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

QUEUE_DIR = Path("queue")
PUBLISHED_DIR = Path("published")
DEFAULT_CHANNEL = "@telezhukkk"


def send_message(token: str, channel: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": channel,
        "text": text,
        "disable_web_page_preview": "false",
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        # Telegram отдаёт тело ошибки в JSON даже при 4xx/5xx — читаем его,
        # а не просто падаем на статусе, иначе причина ошибки теряется
        return json.loads(e.read().decode())


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    # `or DEFAULT_CHANNEL`, а не .get(..., default) — GitHub Actions передаёт
    # незаданную vars.* как пустую строку, а не отсутствующую переменную
    channel = os.environ.get("TELEGRAM_CHANNEL") or DEFAULT_CHANNEL

    if not token:
        print("Ошибка: TELEGRAM_BOT_TOKEN не задан", file=sys.stderr)
        sys.exit(1)

    QUEUE_DIR.mkdir(exist_ok=True)
    PUBLISHED_DIR.mkdir(exist_ok=True)

    files = sorted(QUEUE_DIR.glob("*.txt"))
    if not files:
        print("Очередь пуста — публиковать нечего. Добавь .txt-файлы в queue/.")
        sys.exit(0)

    next_file = files[0]
    text = next_file.read_text(encoding="utf-8").strip()

    if not text:
        print(f"Ошибка: {next_file.name} пустой, пропускаю без публикации", file=sys.stderr)
        sys.exit(1)

    result = send_message(token, channel, text)

    if not result.get("ok"):
        print(f"Ошибка публикации в {channel}: {result}", file=sys.stderr)
        sys.exit(1)

    msg_id = result["result"]["message_id"]
    print(f"Опубликовано {next_file.name} -> {channel}, message_id={msg_id}")

    dest = PUBLISHED_DIR / next_file.name
    next_file.rename(dest)


if __name__ == "__main__":
    main()

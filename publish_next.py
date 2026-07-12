#!/usr/bin/env python3
"""
Раз в 2 дня публикует следующий пост из очереди в Telegram-канал: фото с подписью.
Берёт первый файл queue/*.json (сортировка по имени), отправляет через sendPhoto,
переносит файл в published/ и обновляет state.json с датой последней публикации.

Запускается ежедневно из GitHub Actions, но публикует только если с прошлой
публикации прошло 2 или больше дней. Так интервал "через день" держится точно,
без сбоев на границах месяца, в отличие от cron с фиксированными днями недели.

Переменные окружения:
    TELEGRAM_BOT_TOKEN — токен бота (хранить в GitHub Secrets, не в коде)
    TELEGRAM_CHANNEL    — username канала, по умолчанию @telezhukkk
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

QUEUE_DIR = Path("queue")
PUBLISHED_DIR = Path("published")
STATE_FILE = Path("state.json")
INTERVAL_DAYS = 2
MOSCOW = timezone(timedelta(hours=3))


def moscow_today() -> date:
    return datetime.now(MOSCOW).date()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def send_photo(token: str, channel: str, image_url: str, caption: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = urllib.parse.urlencode({
        "chat_id": channel,
        "photo": image_url,
        "caption": caption,
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    channel = os.environ.get("TELEGRAM_CHANNEL", "@telezhukkk")

    if not token:
        print("Ошибка: TELEGRAM_BOT_TOKEN не задан", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    last_published_str = state.get("last_published")
    today = moscow_today()

    if last_published_str:
        last_published = date.fromisoformat(last_published_str)
        days_passed = (today - last_published).days
        if days_passed < INTERVAL_DAYS:
            print(f"Ещё не пора: с прошлой публикации прошло {days_passed} дн., нужно {INTERVAL_DAYS}.")
            sys.exit(0)

    QUEUE_DIR.mkdir(exist_ok=True)
    PUBLISHED_DIR.mkdir(exist_ok=True)

    files = sorted(QUEUE_DIR.glob("*.json"))
    if not files:
        print("Очередь пуста, публиковать нечего. Добавь новые файлы в queue/.")
        sys.exit(0)

    next_file = files[0]
    post = json.loads(next_file.read_text(encoding="utf-8"))
    caption = post["caption"].strip()
    image_url = post["image"]

    result = send_photo(token, channel, image_url, caption)

    if not result.get("ok"):
        print(f"Ошибка публикации: {result}", file=sys.stderr)
        sys.exit(1)

    msg_id = result["result"]["message_id"]
    print(f"Опубликовано {next_file.name} -> message_id={msg_id}")

    dest = PUBLISHED_DIR / next_file.name
    next_file.rename(dest)

    state["last_published"] = today.isoformat()
    save_state(state)


if __name__ == "__main__":
    main()

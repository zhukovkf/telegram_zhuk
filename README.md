# Автопостинг в Telegram-канал

Кладёте текстовые посты в `queue/`, GitHub Actions по расписанию публикует
следующий по очереди в канал `@telezhukkk` и переносит файл в `published/`.
Без сервера — работает целиком на бесплатных GitHub Actions.

## Как это устроено

- `queue/` — очередь: `.txt`-файлы с текстом постов. Публикуются по одному,
  в алфавитном порядке имён файлов (поэтому имена стоит нумеровать, например
  `01-anons.txt`, `02-novost.txt`).
- `published/` — сюда переезжает файл сразу после публикации (так очередь
  не публикует один и тот же пост дважды).
- `publish_next.py` — берёт первый файл из `queue/`, публикует его текст в
  канал через Telegram Bot API и переносит в `published/`.
- `.github/workflows/publish.yml` — по расписанию (пн/ср/пт, 09:00 МСК)
  запускает `publish_next.py` и коммитит перемещение файла обратно в
  репозиторий. Можно запустить и вручную: Actions → Publish Telegram Post
  → Run workflow.

## Настройка (один раз)

1. **Бот.** Если ещё нет бота — напишите **@BotFather** в Telegram,
   `/newbot`, задайте имя. Он выдаст токен вида `123456:AAExxxxxxxx` —
   сохраните его, он понадобится на шаге 3.
2. **Права бота в канале.** Откройте канал `@telezhukkk` → Administrators →
   Add Admin → выберите вашего бота → включите право **Post Messages**.
   Без этого публикация будет падать с ошибкой `Forbidden`.
3. **Секрет репозитория.** В репозитории: Settings → Secrets and variables
   → Actions → New repository secret → имя `TELEGRAM_BOT_TOKEN`, значение —
   токен из шага 1.
4. Канал `@telezhukkk` уже стоит по умолчанию в коде. Если захотите постить
   в другой канал — не меняя код, добавьте туда же (Secrets and variables →
   Actions) вкладку **Variables** → New repository variable → имя
   `TELEGRAM_CHANNEL`, значение — username нового канала.

## Как добавить пост

1. Создайте `.txt`-файл в `queue/` с текстом поста (можно через веб-интерфейс
   GitHub: Add file → Create new file).
2. Закоммитьте — пост опубликуется при следующем срабатывании расписания,
   либо запустите workflow вручную (Actions → Publish Telegram Post → Run
   workflow), чтобы не ждать.

## Локальный тест (без GitHub Actions)

```
export TELEGRAM_BOT_TOKEN=xxxx
python3 publish_next.py
```

Если очередь пуста, скрипт просто сообщит об этом и ничего не сделает.

## Расписание

По умолчанию — пн/ср/пт в 09:00 по Москве. Меняется строкой `cron` в
`.github/workflows/publish.yml` (время в cron — UTC, Москва = UTC+3).

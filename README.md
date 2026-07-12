# Автопостинг в Telegram-канал

Кладёте посты (текст + картинка) в `queue/`, GitHub Actions раз в 2 дня публикует следующий по очереди в канал @telezhukkk и переносит файл в `published/`. Без сервера, работает целиком на бесплатных GitHub Actions.

## Как это устроено

- `queue/` — очередь: `.json`-файлы вида `{"image": "<url картинки>", "caption": "<текст поста>"}`. Публикуются по одному, в алфавитном порядке имён файлов (поэтому имена нумеруются: `07.json`, `08.json`...).
- `published/` — сюда переезжает файл сразу после публикации, чтобы очередь не публиковала один и тот же пост дважды.
- `state.json` — дата последней публикации. По ней скрипт считает, прошло ли 2 дня с прошлого поста.
- `publish_next.py` — раз в день проверяет `state.json`; если прошло 2 дня и больше, берёт первый файл из `queue/`, публикует фото с подписью через Telegram Bot API (`sendPhoto`), переносит файл в `published/` и обновляет `state.json`.
- `.github/workflows/publish.yml` — по расписанию (каждый день в 09:00 МСК) запускает `publish_next.py` и коммитит изменения обратно в репозиторий. Можно запустить и вручную: Actions → Publish Telegram Post → Run workflow.

## Настройка (один раз)

1. **Бот.** Если ещё нет — напишите @BotFather в Telegram, `/newbot`, задайте имя. Он выдаст токен вида `123456:AAExxxxxxxx`.
2. **Права бота в канале.** Откройте канал @telezhukkk → Administrators → Add Admin → выберите бота → включите право Post Messages.
3. **Секрет репозитория.** Settings → Secrets and variables → Actions → New repository secret → имя `TELEGRAM_BOT_TOKEN`, значение — токен из шага 1.
4. **Права workflow на запись.** Settings → Actions → General → Workflow permissions → Read and write permissions → Save.

Канал `@telezhukkk` стоит по умолчанию в коде. Чтобы постить в другой канал без изменения кода, добавьте переменную репозитория (Secrets and variables → Actions → Variables → New repository variable) с именем `TELEGRAM_CHANNEL`.

## Как добавить пост

1. Создайте `.json`-файл в `queue/` (Add file → Create new file), например `47.json`:
   ```json
   {
     "image": "https://images.unsplash.com/photo-xxxx?w=1200&q=80",
     "caption": "Текст поста, до 1024 символов."
   }
   ```
2. Закоммитьте. Пост опубликуется по расписанию (раз в 2 дня) либо сразу, если запустить workflow вручную.

## Локальный тест (без GitHub Actions)

```bash
export TELEGRAM_BOT_TOKEN=xxxx
python3 publish_next.py
```

Если с прошлой публикации прошло меньше 2 дней, скрипт сообщит об этом и ничего не отправит. Если очередь пуста, тоже просто сообщит и ничего не сделает.

## Расписание

Интервал 2 дня задан в `publish_next.py` (переменная `INTERVAL_DAYS`) и проверяется каждый день, поэтому он не сбивается на границах месяца, в отличие от cron с фиксированными днями недели. Время проверки — в `.github/workflows/publish.yml` (cron в UTC, Москва = UTC+3).

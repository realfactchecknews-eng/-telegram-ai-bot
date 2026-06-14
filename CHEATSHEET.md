# Шпаргалка по боту

## Где лежат файлы

```
/var/folders/v7/jdx2nhzn39l7h1l7_7zyyhb00000gn/T/opencode/telegram-ai-bot/
```

## Главные файлы

- `bot.py` — сам бот. Тут меняется стиль, промпт, API.
- `requirements.txt` — библиотеки.
- `.env` — токены и ключи (не публикуется в GitHub).
- `.env.example` — шаблон `.env`.
- `.gitignore` — файлы, которые не попадают в Git.
- `README.md` — полная инструкция.

## Быстрый запуск

```bash
cd /var/folders/v7/jdx2nhzn39l7h1l7_7zyyhb00000gn/T/opencode/telegram-ai-bot/
python3 -m pip install -r requirements.txt
python3 bot.py
```

Остановить бота: `Ctrl + C` в терминале.

## Как открыть `.env`

```bash
open .env
```

Или через Finder: `Cmd + Shift + G` → вставить путь к папке.

## Какие API сейчас поддерживаются

Бот пробует API по очереди. Достаточно заполнить один ключ в `.env`. Если все ключи пустые или не работают, бот переключается в тестовый режим и всё равно отвечает.

- `GROQ_API_KEY` — бесплатный, сейчас работает.
- `HUGGINGFACE_API_KEY` — бесплатный.
- `CEREBRAS_API_KEY` — бесплатный.
- `TOGETHER_API_KEY` — $5 кредитов на старте.
- `OPENROUTER_API_KEY` — платный, но дёшево.

Чтобы отключить API, поставь `#` в начале строки:

```bash
# GROQ_API_KEY=...
```

## Как подключить другую нейросеть

1. Найди API-документацию нейросети.
2. Добавь новую функцию в `bot.py` рядом с `ask_groq`, `ask_gemini` и т.д.
3. Добавь ключ в `.env` и в `.env.example`.
4. Добавь проверку ключа и функцию в список `providers` внутри `ask_ai()`.
5. Проверь, что формат запроса совпадает с документацией (OpenAI-совместимый или свой).

## Где меняется стиль и фразы

В файле `bot.py` ищи два блока:

### Системный промпт (строки 24–32)

```python
SYSTEM_PROMPT = (
    "Ты отвечаешь на русском языке в стиле стримера Мелстроя..."
)
```

Здесь меняется общий стиль: язык, тон, часто используемые слова.

### Примеры фраз (строки 34–57)

```python
FEW_SHOT_EXAMPLES = [
    {"role": "user", "content": "Привет"},
    {"role": "assistant", "content": "Здарова, беды 👋"},
    ...
]
```

Здесь вставляются конкретные фразы. Чем больше примеров — тем точнее стиль.

## Где меняется приветствие по команде `/start`

В файле `bot.py` ищи:

```python
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Здарова беды, шо вы боровы? Пошла возня возняцкая 🔥"
    )
```

## Как запушить изменения на GitHub

После любых правок в коде:

```bash
cd /var/folders/v7/jdx2nhzn39l7h1l7_7zyyhb00000gn/T/opencode/telegram-ai-bot/
git add .
git commit -m "Описание изменений"
git push
```

## Где задеплоен бот

- Репозиторий: https://github.com/realfactchecknews-eng/-telegram-ai-bot
- Хостинг: https://bothost.ru/

После пуша в GitHub Bothost автоматически перезапускает бота, если настроен авто-деплой.

## Что делать, если ошибка SSL

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

Замени `3.13` на свою версию Python.

## Полезные ссылки

- Groq: https://console.groq.com/keys
- Gemini: https://aistudio.google.com/app/apikey
- HuggingFace: https://huggingface.co/settings/tokens
- Cerebras: https://cloud.cerebras.ai/
- Together: https://api.together.xyz/
- OpenRouter: https://openrouter.ai/
- BotFather: https://t.me/BotFather

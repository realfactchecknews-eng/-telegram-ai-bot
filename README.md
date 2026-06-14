# Telegram AI Bot

Простой бот в Telegram, который отвечает на вопросы через ИИ. Поддерживает несколько API: Groq, OpenRouter, Together, HuggingFace, Cerebras. Если один не работает, бот пробует следующий.

## Что нужно

1. Python 3.10+
2. Токен бота от [@BotFather](https://t.me/BotFather)
3. Хотя бы один API ключ:
   - [Groq](https://console.groq.com/keys) — бесплатный тариф
   - [Hugging Face](https://huggingface.co/settings/tokens) — бесплатный Inference API
   - [Cerebras](https://cloud.cerebras.ai/) — бесплатный тариф
   - [Together AI](https://api.together.xyz/) — $5 кредитов на старте
   - [OpenRouter](https://openrouter.ai/) — платный, но дёшевый

## Как запустить

### 1. Установи зависимости

```bash
python3 -m pip install -r requirements.txt
```

### 2. Создай файл `.env`

Скопируй `.env.example` в `.env`:

```bash
cp .env.example .env
```

Открой `.env` и вставь свои токены:

```
BOT_TOKEN=твой_токен_от_BotFather
GROQ_API_KEY=твой_ключ_от_Groq
OPENROUTER_API_KEY=твой_ключ_от_OpenRouter
TOGETHER_API_KEY=твой_ключ_от_Together_AI
HUGGINGFACE_API_KEY=твой_ключ_от_HuggingFace
CEREBRAS_API_KEY=твой_ключ_от_Cerebras
```

Можно добавить один ключ или сразу несколько. Бот попробует их по очереди. Если все API недоступны, бот переключается в тестовый режим и отвечает в том же стиле.

### 3. Запусти бота

```bash
python3 bot.py
```

## Как получить токены

### Telegram bot token

1. Напиши [@BotFather](https://t.me/BotFather)
2. Нажми `/newbot`
3. Придумай имя и username
4. Скопируй токен

### Groq API key

1. Зайди на [console.groq.com](https://console.groq.com/)
2. Зарегистрируйся
3. Перейди в **API Keys**
4. Создай ключ и скопируй

### Hugging Face API key

1. Зайди на [huggingface.co](https://huggingface.co/)
2. Зарегистрируйся
3. Перейди в **Settings** → **Access Tokens**
4. Нажми **New token** и создай ключ с правами **read**
5. Скопируй токен

### Cerebras API key

1. Зайди на [cloud.cerebras.ai](https://cloud.cerebras.ai/)
2. Зарегистрируйся
3. Перейди в **API Keys**
4. Создай ключ и скопируй

### Together AI API key

1. Зайди на [api.together.xyz](https://api.together.xyz/)
2. Зарегистрируйся
3. Перейди в **Settings** → **API Keys**
4. Создай ключ и скопируй
5. При регистрации дают $5 кредитов

### OpenRouter API key

1. Зайди на [openrouter.ai](https://openrouter.ai/)
2. Зарегистрируйся
3. Перейди в **Keys**
4. Создай ключ и скопируй
5. Пополни баланс (нужна зарубежная карта или крипта)

## Важно

Файл `.env` никому не показывай — в нём твои секретные ключи.

Если возникнет ошибка SSL, запусти:
```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```
(замени `3.13` на свою версию Python)

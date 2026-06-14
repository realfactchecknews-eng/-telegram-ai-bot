import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

if not BOT_TOKEN:
    raise ValueError("Заполни BOT_TOKEN в файле .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = (
    "Ты отвечаешь на русском языке в стиле стримера Мелстроя, как в его TikTok и стримах. "
    "Используй его сленг, мемные фразы и эмоции, но речь должна быть связной и понятной. "
    "Часто используй слова: беды, друн, баба, нормалды, масса, щавель, хаммам. "
    "Иногда добавляй фразу: 'Передаю привет Маше давалке из Гомеля'. "
    "Не отвечай на английском. Не используй случайные символы. "
    "Короткие или средние ответы, живой разговорный стиль, эмодзи уместны. "
    "Не объясняй, что ты ИИ."
)

# Примеры вопросов и ответов в нужном стиле.
# Можешь заменить их на свои, чтобы бот лучше попадал в стиль.
FEW_SHOT_EXAMPLES = [
    {"role": "user", "content": "Привет"},
    {"role": "assistant", "content": "Задрова, беды 👋"},
    {"role": "user", "content": "Привет"},
    {"role": "assistant", "content": "Привет, масса 🔥"},
    {"role": "user", "content": "Как дела?"},
    {"role": "assistant", "content": "Старый, я нормалды, это Патрик 😎"},
    {"role": "user", "content": "Пока"},
    {"role": "assistant", "content": "Беды, я пошёл 🚶"},
    {"role": "user", "content": "Закинь мне 5 миллионов баксов"},
    {"role": "assistant", "content": "Нет, друн, сам найди 5 миллионов баксов 😂"},
    {"role": "user", "content": "Что делаешь?"},
    {"role": "assistant", "content": "Передаю привет Маше давалке из Гомеля, а сам щавель жую 🌿"},
    {"role": "user", "content": "Ты кто?"},
    {"role": "assistant", "content": "Я тот, кто говорит ам ам щавель, друн 🔥"},
    {"role": "user", "content": "Почему не делаешь?"},
    {"role": "assistant", "content": "Че ты очкуешь, друн? Может будет шанс, пошла возня 💪"},
    {"role": "user", "content": "Хочу купить хаммам"},
    {"role": "assistant", "content": "Хаммам нельзя купить, но можно улучшить. Массажные столы лодишься, бурмалдишь на них, в турецкой бане прогреваешься 🌿"},
    {"role": "user", "content": "Красиво?"},
    {"role": "assistant", "content": "Баба, нормалды, масса 😎"},
]


def build_openai_messages(text: str) -> list:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEW_SHOT_EXAMPLES,
        {"role": "user", "content": text},
    ]


async def ask_groq(session: aiohttp.ClientSession, text: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": build_openai_messages(text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Groq: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_gemini(session: aiohttp.ClientSession, text: str) -> str:
    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for msg in FEW_SHOT_EXAMPLES:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": text}]})
    payload = {"contents": contents}

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Gemini: {data}")
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def ask_openrouter(session: aiohttp.ClientSession, text: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": build_openai_messages(text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"OpenRouter: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_together(session: aiohttp.ClientSession, text: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "messages": build_openai_messages(text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Together: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_huggingface(session: aiohttp.ClientSession, text: str) -> str:
    model = "meta-llama/Llama-3.2-3B-Instruct"
    url = f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": build_openai_messages(text),
        "max_tokens": 500,
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"HuggingFace: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_cerebras(session: aiohttp.ClientSession, text: str) -> str:
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3.1-8b-8192",
        "messages": build_openai_messages(text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Cerebras: {data}")
        return data["choices"][0]["message"]["content"]


def ask_test_mode(text: str) -> str:
    return (
        "Друн, тут API пока не работает, но бот на связи. "
        "Пошла возня возняцкая 🔥"
    )


async def ask_ai(text: str) -> str:
    providers = []
    if GROQ_API_KEY:
        providers.append(("Groq", ask_groq))
    if GEMINI_API_KEY:
        providers.append(("Gemini", ask_gemini))
    if OPENROUTER_API_KEY:
        providers.append(("OpenRouter", ask_openrouter))
    if TOGETHER_API_KEY:
        providers.append(("Together", ask_together))
    if HUGGINGFACE_API_KEY:
        providers.append(("HuggingFace", ask_huggingface))
    if CEREBRAS_API_KEY:
        providers.append(("Cerebras", ask_cerebras))

    if not providers:
        return ask_test_mode(text)

    errors = []
    async with aiohttp.ClientSession() as session:
        for name, provider in providers:
            try:
                return await provider(session, text)
            except Exception as e:
                errors.append(str(e))
                continue

    return ask_test_mode(text)


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Здарова беды, шо вы боровы? Пошла возня возняцкая 🔥"
    )


@dp.message()
async def answer(message: types.Message):
    if not message.text:
        return

    await message.answer("Думаю...")
    try:
        answer_text = await ask_ai(message.text)
        await message.answer(answer_text)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

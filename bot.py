import asyncio
import os
import random
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import aiohttp

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
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
    "Не объясняй, что ты ИИ. "
    "Помни контекст разговора и отвечай в общем стиле."
)

# Примеры вопросов и ответов в нужном стиле.
# Можешь заменить их на свои или добавить ещё, чтобы бот лучше попадал в стиль.
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
    {"role": "user", "content": "Кто такая Маша?"},
    {"role": "assistant", "content": "Маша — давалка из Гомеля, друн, все знают 😂"},
    {"role": "user", "content": "Что по щавелю?"},
    {"role": "assistant", "content": "Ам ам щавель, беды, вкуснятина 🌿"},
    {"role": "user", "content": "Какой час?"},
    {"role": "assistant", "content": "13:56, поезд отправляется, дядя Корэе на связи 🚂"},
]

CATCHPHRASES = [
    "Друн, ",
    "Беды, ",
    "Масса, ",
    "Ам ам щавель, ",
    "Плаки плаки нормалдаки, ",
    "Пошла возня, ",
    "Че ты очкуешь, ",
    "Передаю привет Маше давалке из Гомеля, ",
]

# История диалогов: {user_id: [messages]}
chat_history = {}
MAX_HISTORY = 10


def get_system_prompt() -> str:
    catchphrase = random.choice(CATCHPHRASES)
    return f"{SYSTEM_PROMPT} Начинай ответ с: '{catchphrase}'"


def build_openai_messages(user_id: int, text: str) -> list:
    history = chat_history.get(user_id, [])
    messages = [
        {"role": "system", "content": get_system_prompt()},
        *FEW_SHOT_EXAMPLES,
        *history,
        {"role": "user", "content": text},
    ]
    return messages


def add_to_history(user_id: int, role: str, content: str):
    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append({"role": role, "content": content})
    if len(chat_history[user_id]) > MAX_HISTORY:
        chat_history[user_id] = chat_history[user_id][-MAX_HISTORY:]


async def ask_groq(session: aiohttp.ClientSession, user_id: int, text: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": build_openai_messages(user_id, text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Groq: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_openrouter(session: aiohttp.ClientSession, user_id: int, text: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": build_openai_messages(user_id, text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"OpenRouter: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_deepseek(session: aiohttp.ClientSession, user_id: int, text: str) -> str:
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": build_openai_messages(user_id, text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"DeepSeek: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_together(session: aiohttp.ClientSession, user_id: int, text: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "messages": build_openai_messages(user_id, text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Together: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_huggingface(session: aiohttp.ClientSession, user_id: int, text: str) -> str:
    model = "meta-llama/Llama-3.2-3B-Instruct"
    url = f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": build_openai_messages(user_id, text),
        "max_tokens": 500,
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"HuggingFace: {data}")
        return data["choices"][0]["message"]["content"]


async def ask_cerebras(session: aiohttp.ClientSession, user_id: int, text: str) -> str:
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3.1-8b-8192",
        "messages": build_openai_messages(user_id, text),
    }

    async with session.post(url, headers=headers, json=payload) as response:
        data = await response.json()
        if response.status != 200:
            raise RuntimeError(f"Cerebras: {data}")
        return data["choices"][0]["message"]["content"]


def ask_test_mode(user_id: int, text: str) -> str:
    return (
        "Друн, тут API пока не работает, но бот на связи. "
        "Пошла возня возняцкая 🔥"
    )


async def ask_ai(user_id: int, text: str) -> str:
    providers = []
    if OPENROUTER_API_KEY:
        providers.append(("OpenRouter", ask_openrouter))
    if DEEPSEEK_API_KEY:
        providers.append(("DeepSeek", ask_deepseek))
    if GROQ_API_KEY:
        providers.append(("Groq", ask_groq))
    if TOGETHER_API_KEY:
        providers.append(("Together", ask_together))
    if HUGGINGFACE_API_KEY:
        providers.append(("HuggingFace", ask_huggingface))
    if CEREBRAS_API_KEY:
        providers.append(("Cerebras", ask_cerebras))

    if not providers:
        return ask_test_mode(user_id, text)

    errors = []
    async with aiohttp.ClientSession() as session:
        for name, provider in providers:
            print(f"Пробуем API: {name}")
            try:
                result = await provider(session, user_id, text)
                print(f"API {name} отработал")
                return result
            except Exception as e:
                print(f"API {name} ошибка: {e}")
                errors.append(str(e))
                continue

    print("Все API недоступны, переключаемся в тестовый режим")
    return ask_test_mode(user_id, text)


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Здарова беды, шо вы боровы? Пошла возня возняцкая 🔥"
    )


@dp.message()
async def answer(message: types.Message):
    if not message.text:
        return

    user_id = message.from_user.id
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        answer_text = await ask_ai(user_id, message.text)
        add_to_history(user_id, "user", message.text)
        add_to_history(user_id, "assistant", answer_text)
        await message.answer(answer_text)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


async def main():
    print("Бот запущен")
    print(f"OpenRouter API key: {'настроен' if OPENROUTER_API_KEY else 'не настроен'}")
    print(f"OpenRouter model: {OPENROUTER_MODEL}")
    print(f"DeepSeek API key: {'настроен' if DEEPSEEK_API_KEY else 'не настроен'}")
    print(f"Groq API key: {'настроен' if GROQ_API_KEY else 'не настроен'}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

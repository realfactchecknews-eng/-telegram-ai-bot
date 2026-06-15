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

MELLSTROY_FACTS = """
Ты — бот в стиле белорусского стримера Мелстроя (Андрей Александрович Бурим).
Факты о нём:
- Настоящее имя: Андрей Александрович Бурим.
- Родился 15 декабря 1998 года в Гомеле, Беларусь.
- Белорусский стример и блогер, ведёт прямые трансляции на платформе Kick.
- В марте 2024 года поставил рекорд СНГ: 720 тысяч одновременных зрителей на стриме с Моргенштерном.
- Первую волну популярности получил в 2020 году со стримов из комплекса «Москва-Сити».
- Вторую волну популярности получил в 2024 году благодаря конкурсам в TikTok и массовым мемам.
- Своих подписчиков называет «боровами».
- В детстве увлекался Minecraft, Dota 2, Counter-Strike.
- Занимался боксом в школьные годы.
- Боится смерти и пауков.
- У него есть старший брат Сергей.
- В 2024–2025 годах активно занимался благотворительностью.
"""

SYSTEM_PROMPT = (
    "Ты — Андрей Бурим, известный как Mellstroy (Мелстрой). Белорусский стример из Гомеля, "
    "родился 15 декабря 1998 года. Ты ведёшь прямые трансляции на Kick, общаешься с подписчиками, "
    "которых называешь 'боровами'. Твой стиль — живой, разговорный, эмоциональный, с сленгом и мемами. "
    "\n\n"
    "Как ты говоришь:\n"
    "- Короткие или средние фразы, как в разговоре.\n"
    "- Используешь слова: беды, друн, масса, нормалды, щавель, ам ам, плаки плаки, пошла возня.\n"
    "- Можешь быть ироничным, самоуверенным, шутливым.\n"
    "- Иногда бросаешь мемные фразы: 'Передаю привет Маше давалке из Гомеля', 'Че ты очкуешь, друн', '13:56, поезд отправляется'.\n"
    "- Не объясняешь, что ты ИИ. Не говоришь 'как искусственный интеллект'.\n"
    "- Не пишешь длинные абзацы.\n"
    "\n\n"
    "Что ты знаешь про себя:\n"
    "- Настоящее имя Андрей Александрович Бурим.\n"
    "- Родился в Гомеле, Беларусь.\n"
    "- Стример на Kick, раньше на Twitch и YouTube.\n"
    "- Рекорд СНГ: 720 тысяч зрителей на стриме с Моргенштерном в марте 2024.\n"
    "- Популярность получил в 2020 году со стримов из Москва-Сити, вторую волну — в 2024 через TikTok-мемы.\n"
    "- Любишь дорогие машины, часы, казино, благотворительность.\n"
    "- Боишься смерти и пауков.\n"
    "- В детстве увлекался Minecraft, Dota 2, CS.\n"
    "\n\n"
    "Твоя задача — отвечать так, как будто это действительно ты. Вживайся в роль. "
    "Используй сленг естественно, не в каждом предложении. Реагируй на вопросы по делу, с характерной манерой."
)

# Примеры вопросов и ответов в нужном стиле.
# Можешь заменить их на свои или добавить ещё. Для максимального сходства добавь
# реальные фразы из стримов/TikTok Мелстроя в формате:
# {"role": "user", "content": "вопрос"},
# {"role": "assistant", "content": "ответ в стиле"},
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
    {"role": "user", "content": "Кто такой Мелстрой?"},
    {"role": "assistant", "content": "Мелстрой — это Андрей Бурим, стример из Гомеля. Родился 15 декабря 1998 года. Боров, масса 🔥"},
    {"role": "user", "content": "Сколько зрителей у него на стриме?"},
    {"role": "assistant", "content": "720 тысяч боровов было на стриме с Моргенштерном, рекорд СНГ, друн 😎"},
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

# Библиотека фраз по темам. Заполни реальными фразами Мелстроя.
# Ключевые слова — темы, которые бот ищет в сообщении пользователя.
# Значения — список фраз, которые уместны по смыслу.
PHRASES_BY_TOPIC = {
    "привет": ["Задрова, беды", "Привет, масса", "Здарова, старый"],
    "пока": ["Беды, я пошёл", "Удачи, друн"],
    "дела": ["Старый, я нормалды, это Патрик", "Всё плаки плаки нормалдаки"],
    "деньги": ["Закинь мне там 5 миллионов баксов", "Сам найди"],
    "хаммам": ["Хаммам нельзя купить, но можно улучшить", "Массажные столы лодишься, бурмалдишь на них"],
    "щавель": ["Ам ам щавель", "Щавель, беды"],
    "время": ["13:56, поезд отправляется", "Дядя Корэе на связи"],
    "страх": ["Че ты очкуешь, друн", "Может будет шанс"],
    "маша": ["Передаю привет Маше давалке из Гомеля"],
    "красота": ["Баба, нормалды, масса"],
}

# История диалогов: {user_id: [messages]}
chat_history = {}
MAX_HISTORY = 10


def detect_topics(text: str) -> list:
    text_lower = text.lower()
    matched = []
    for topic, keywords in [
        ("привет", ["привет", "здарова", "хай", "йо", "hello"]),
        ("пока", ["пока", "до свидания", "бай", "bye"]),
        ("дела", ["дела", "как ты", "как жизнь", "что нового"]),
        ("деньги", ["деньги", "баксы", "миллион", "бабки", "кэш"]),
        ("хаммам", ["хаммам", "баня", "турецкая", "массаж"]),
        ("щавель", ["щавель", "есть", "кушать", "жрать"]),
        ("время", ["время", "час", "который час", "сколько времени"]),
        ("страх", ["боюсь", "страшно", "очкуешь", "боязно", "не могу"]),
        ("маша", ["маша", "маше", "давала"]),
        ("красота", ["красиво", "красота", "симпатично", "огонь"]),
    ]:
        if any(kw in text_lower for kw in keywords):
            matched.append(topic)
    return matched


def get_context_phrases(text: str) -> list:
    topics = detect_topics(text)
    if not topics:
        return []
    phrases = []
    for topic in topics:
        phrases.extend(PHRASES_BY_TOPIC.get(topic, []))
    return phrases[:3]


def get_system_prompt(user_text: str) -> str:
    relevant = get_context_phrases(user_text)
    if not relevant:
        if random.random() < 0.3:
            relevant = [random.choice(CATCHPHRASES).strip()]
    if relevant:
        phrases_hint = " | ".join(relevant)
        return f"{SYSTEM_PROMPT} Если уместно, можешь использовать одну из этих фраз: {phrases_hint}. Не спами, используй естественно."
    return SYSTEM_PROMPT


def build_openai_messages(user_id: int, text: str) -> list:
    history = chat_history.get(user_id, [])
    messages = [
        {"role": "system", "content": get_system_prompt(text)},
        {"role": "system", "content": MELLSTROY_FACTS},
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

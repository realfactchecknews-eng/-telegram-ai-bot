"""
Скрипт собирает видео по заданным хэштегам/поисковым запросам в TikTok,
транскрибирует речь и сохраняет текст в папку output/.

Использование:
    python tiktok_collector.py

Настрой список ЗАПРОСЫ ниже под себя.
"""

import os
import subprocess
import json
import datetime

# ---------- НАСТРОЙКИ ----------

# Хэштеги или поисковые запросы (без решётки можно тоже)
ЗАПРОСЫ = [
    "#mellstroy",
    "#мелстрой",
    "мелстрой мемы",
]

# Сколько видео максимум скачивать за один запуск на каждый запрос
МАКС_ВИДЕО_НА_ЗАПРОС = 10

# Папка для результатов
ВЫХОДНАЯ_ПАПКА = "output"

# Временная папка для видео (будут удаляться после транскрибации)
ВРЕМЕННАЯ_ПАПКА = "tmp_videos"

# Модель Whisper: tiny / base / small / medium / large
# base — хороший баланс скорости и качества для русского языка
WHISPER_МОДЕЛЬ = "base"

# --------------------------------


def скачать_видео(запрос, лимит):
    """Скачивает видео по запросу через yt-dlp, возвращает список путей к файлам."""
    папка = os.path.join(ВРЕМЕННАЯ_ПАПКА, запрос.replace("#", "").replace(" ", "_"))
    os.makedirs(папка, exist_ok=True)

    # Поисковый запрос в формате yt-dlp для TikTok
    search_query = f"tiktoksearch{лимит}:{запрос}"

    команда = [
        "yt-dlp",
        search_query,
        "-o", os.path.join(папка, "%(id)s.%(ext)s"),
        "--write-info-json",
        "--no-warnings",
        "--ignore-errors",
    ]

    print(f"[*] Скачиваю по запросу: {запрос}")
    subprocess.run(команда, check=False)

    видео_файлы = []
    for f in os.listdir(папка):
        if f.endswith((".mp4", ".webm")):
            видео_файлы.append(os.path.join(папка, f))
    return видео_файлы


def получить_метаданные(путь_видео):
    """Читает info.json рядом с видео, возвращает ссылку и описание."""
    info_путь = os.path.splitext(путь_видео)[0] + ".info.json"
    if os.path.exists(info_путь):
        with open(info_путь, "r", encoding="utf-8") as f:
            данные = json.load(f)
        return {
            "ссылка": данные.get("webpage_url", ""),
            "описание": данные.get("description", ""),
            "автор": данные.get("uploader", ""),
        }
    return {"ссылка": "", "описание": "", "автор": ""}


def транскрибировать(путь_видео, модель):
    """Запускает whisper и возвращает текст транскрипта."""
    print(f"    -> Транскрибирую: {os.path.basename(путь_видео)}")
    результат = subprocess.run(
        ["whisper", путь_видео, "--model", модель, "--language", "ru",
         "--output_format", "txt", "--output_dir", ВРЕМЕННАЯ_ПАПКА, "--fp16", "False"],
        capture_output=True, text=True
    )
    txt_путь = os.path.splitext(путь_видео)[0] + ".txt"
    txt_путь = os.path.join(ВРЕМЕННАЯ_ПАПКА, os.path.basename(txt_путь))
    if os.path.exists(txt_путь):
        with open(txt_путь, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def главная():
    os.makedirs(ВЫХОДНАЯ_ПАПКА, exist_ok=True)
    os.makedirs(ВРЕМЕННАЯ_ПАПКА, exist_ok=True)

    дата = datetime.date.today().isoformat()
    итоговый_файл = os.path.join(ВЫХОДНАЯ_ПАПКА, f"фразы_{дата}.md")

    записи = []

    for запрос in ЗАПРОСЫ:
        видео_файлы = скачать_видео(запрос, МАКС_ВИДЕО_НА_ЗАПРОС)

        for путь in видео_файлы:
            мета = получить_метаданные(путь)
            текст = транскрибировать(путь, WHISPER_МОДЕЛЬ)

            if текст:
                записи.append({
                    "запрос": запрос,
                    "ссылка": мета["ссылка"],
                    "автор": мета["автор"],
                    "текст": текст,
                })

            # Удаляем видео и временные файлы после обработки
            for доп_расширение in [".mp4", ".webm", ".txt", ".info.json", ".srt", ".vtt", ".json"]:
                кандидат = os.path.splitext(путь)[0] + доп_расширение
                if os.path.exists(кандидат):
                    os.remove(кандидат)
                кандидат_tmp = os.path.join(ВРЕМЕННАЯ_ПАПКА, os.path.basename(кандидат))
                if os.path.exists(кандидат_tmp):
                    os.remove(кандидат_tmp)

    # Сохраняем результаты в markdown файл
    with open(итоговый_файл, "w", encoding="utf-8") as f:
        f.write(f"# Собранные фразы — {дата}\n\n")
        if not записи:
            f.write("Ничего не найдено за этот запуск.\n")
        for запись in записи:
            f.write(f"## Источник: {запись['запрос']}\n")
            f.write(f"- Автор: {запись['автор']}\n")
            f.write(f"- Ссылка: {запись['ссылка']}\n\n")
            f.write(f"**Транскрипт:**\n\n{запись['текст']}\n\n")
            f.write("---\n\n")

    print(f"\n[+] Готово! Результаты сохранены в: {итоговый_файл}")
    print(f"[+] Найдено записей: {len(записи)}")


if __name__ == "__main__":
    главная()

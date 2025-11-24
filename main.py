import os
import json
import requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

YANDEX_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
if not YANDEX_TOKEN:
    print("❌ Ошибка: не найден токен YANDEX_DISK_TOKEN в файле .env")
    exit(1)

GROUP_FOLDER = "PY-140"

def get_cat_image_url(text: str) -> str:
    safe_text = quote(text)
    return f"https://cataas.com/cat/says/{safe_text}"

def get_file_size(url: str) -> int:
    try:
        response = requests.head(url)
        return int(response.headers.get("content-length", 0))
    except Exception:
        return 0

def create_folder_on_yadisk(folder_name: str):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    params = {"path": folder_name}
    response = requests.put(url, headers=headers, params=params)
    if response.status_code not in (201, 409):
        raise Exception(f"Не удалось создать папку: {response.text}")

def upload_file_to_yadisk(url: str, yadisk_path: str):
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    params = {
        "path": yadisk_path,
        "url": url,
        "overwrite": "true"
    }
    response = requests.post(upload_url, headers=headers, params=params)
    if response.status_code != 202:
        raise Exception(f"Ошибка загрузки: {response.text}")

def main():
    text = input("🔤 Введите текст для картинки с котом: ").strip()
    if not text:
        print("❌ Текст не может быть пустым!")
        return

    print("🔄 Получаем URL картинки...")
    image_url = get_cat_image_url(text)
    print(f"🖼️  URL: {image_url}")

    filename = f"{text}.jpg"
    invalid_chars = '<>:"/\\|?*'
    clean_filename = "".join(c for c in filename if c not in invalid_chars)
    yadisk_path = f"{GROUP_FOLDER}/{clean_filename}"

    print("📁 Создаём папку на Яндекс.Диске...")
    create_folder_on_yadisk(GROUP_FOLDER)

    print("📤 Загружаем картинку на Яндекс.Диск...")
    upload_file_to_yadisk(image_url, yadisk_path)

    print("📏 Определяем размер файла...")
    size = get_file_size(image_url)

    info = {
        "text": text,
        "filename": clean_filename,
        "yadisk_path": yadisk_path,
        "image_url": image_url,
        "size_bytes": size
    }

    if os.path.exists("backup_info.json"):
        with open("backup_info.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(info)

    with open("backup_info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("✅ Готово! Картинка сохранена на Яндекс.Диске.")
    print(f"📁 Путь на Яндекс.Диске: /{yadisk_path}")
    print(f"📄 Информация сохранена в backup_info.json")

if __name__ == "__main__":
    main()
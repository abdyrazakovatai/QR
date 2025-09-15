from flask import Flask, redirect
import qrcode
import json
import os
import threading
import time
import requests

lock = threading.Lock()

app = Flask(__name__)

PING_INTERVAL = 5 * 60  # 5 минут


def ping_self():
    while True:
        try:
            # Делает GET-запрос на сервер
            requests.get("https://your-server-url.com/ping")
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(PING_INTERVAL)


# Запуск фонового потока
threading.Thread(target=ping_self, daemon=True).start()


# Роут для «пинга»
@app.route("/ping")
def ping():
    return "OK"


# ---------------- НАСТРОЙКИ ----------------
STATS_FILE = "db/db.json"  # файл для хранения статистики
QR_COUNT = 7  # количество QR-кодов
REDIRECT_URL = "https://impatika.com"  # куда будут попадать пользователи после сканирования

# ---------------- ИНИЦИАЛИЗАЦИЯ СЧЁТЧИКОВ ----------------
os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)

counters = {f"qr{i}": 0 for i in range(1, QR_COUNT + 1)}  # дефолт

if os.path.exists(STATS_FILE):
    try:
        with open(STATS_FILE, "r") as f:
            data = f.read().strip()
            if data:  # если файл не пустой
                counters = json.loads(data)
            else:
                print("⚠️ Файл пустой, используем дефолтные счётчики")
    except json.JSONDecodeError:
        print("⚠️ JSON повреждён, пересоздаём счётчики")
        counters = {f"qr{i}": 0 for i in range(1, QR_COUNT + 1)}
        with open(STATS_FILE, "w") as f:
            json.dump(counters, f)
else:
    with open(STATS_FILE, "w") as f:
        json.dump(counters, f)
# ---------------- ФУНКЦИИ ----------------
def save_counters():
    """Сохраняем статистику в файл"""
    with open(STATS_FILE, "w") as f:
        json.dump(counters, f)


def generate_qrs(base_url):
    """
    Генерируем 7 отдельных QR-кодов.
    Каждый QR ведёт на свой URL на твоём сервере.
    """
    for i in range(1, QR_COUNT + 1):
        qr_id = f"qr{i}"
        url = f"{base_url}/{qr_id}"
        img = qrcode.make(url)
        img.save(f"{qr_id}.png")
        print(f"Создан {qr_id}: {url}")


# ---------------- РОУТ ДЛЯ СЧЁТЧИКА ----------------
@app.route("/<qr_id>")
def track(qr_id):
    if qr_id in counters:
        with lock:
            counters[qr_id] += 1  # увеличиваем счётчик конкретного QR
            save_counters()  # сохраняем статистику
        print(f"{qr_id} → {counters[qr_id]} переходов")
        return redirect(REDIRECT_URL)  # редирект на сайт
    return "Неверный QR", 404


# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    # Укажи здесь свой сервер, например Render: https://myapp.onrender.com
    BASE_URL = "https://qr-oolj.onrender.com"
    generate_qrs(BASE_URL)
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

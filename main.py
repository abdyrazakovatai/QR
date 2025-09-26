from flask import Flask, redirect
import qrcode
import os
import threading
import time
import requests

from db.Qr_db import QRStatsDB

# ---------------- НАСТРОЙКИ ----------------
QR_COUNT = 7  # количество QR-кодов
REDIRECT_URL = os.getenv("REDIRECT_URL", "https://impatika.com")  # куда редиректить

# ---------------- ИНИЦИАЛИЗАЦИЯ БД ----------------
db = QRStatsDB(qr_count=QR_COUNT)  # сам создаст таблицу и дефолтные QR

lock = threading.Lock()
app = Flask(__name__)

PING_INTERVAL = 5 * 60  # 5 минут


# ---------------- ФУНКЦИИ ----------------
def ping_self():
    """Периодически пингует сам себя, чтобы Render не засыпал сервис"""
    while True:
        try:
            requests.get(os.getenv("BASE_URL", "https://qr-oolj.onrender.com"))
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(PING_INTERVAL)


def generate_qrs(base_url):
    """
    Генерируем QR-коды qr1..qrN.
    Каждый QR ведёт на свой URL на сервере.
    """
    for i in range(1, QR_COUNT + 1):
        qr_id = f"qr{i}"
        url = f"{base_url}/{qr_id}"
        img = qrcode.make(url)
        img.save(f"{qr_id}.png")
        print(f"Создан {qr_id}: {url}")


# ---------------- РОУТЫ ----------------
@app.route("/ping")
def ping():
    return "OK"


@app.route("/<qr_id>")
def track(qr_id):
    """Роут для редиректа с учётом счётчика"""
    count = db.increment(qr_id)
    if count is not None:
        print(f"{qr_id} → {count} переходов")
        return redirect(REDIRECT_URL)
    return "Неверный QR", 404


# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    BASE_URL = os.getenv("BASE_URL", "https://qr-oolj.onrender.com")
    generate_qrs(BASE_URL)

    # Запуск фонового потока пинга
    threading.Thread(target=ping_self, daemon=True).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
from flask import Flask, redirect
import qrcode
import json
import os

app = Flask(__name__)

# ---------------- НАСТРОЙКИ ----------------
STATS_FILE = "stats.json"  # файл для хранения статистики
QR_COUNT = 7               # количество QR-кодов
REDIRECT_URL = "https://impatika.com"  # куда будут попадать пользователи после сканирования

# ---------------- ИНИЦИАЛИЗАЦИЯ СЧЁТЧИКОВ ----------------
# Если файла со статистикой нет — создаём 7 счётчиков
if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r") as f:
        counters = json.load(f)
else:
    counters = {f"qr{i}": 0 for i in range(1, QR_COUNT + 1)}

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
        counters[qr_id] += 1         # увеличиваем счётчик конкретного QR
        save_counters()              # сохраняем статистику
        print(f"{qr_id} → {counters[qr_id]} переходов")
        return redirect(REDIRECT_URL)  # редирект на сайт
    return "Неверный QR", 404

# ---------------- ЗАПУСК ----------------
if __name__ == "__main__":
    # Укажи здесь свой сервер, например Render: https://myapp.onrender.com
    BASE_URL = "https://.com"

    # Генерируем QR-коды
    generate_qrs(BASE_URL)

    # Запускаем сервер Flask
    app.run(host="0.0.0.0", port=5000, debug=True)

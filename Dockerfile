# Используем Python 3.9
FROM python:3.9-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Порт из Fly.io
ENV PORT 8080

# Запуск приложения
CMD ["python", "main.py"]
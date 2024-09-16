# Використовуємо офіційний образ Python
FROM python:3.11-slim

# Встановлюємо робочий каталог
WORKDIR /app

# Копіюємо файл вимог
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код
COPY . .

# Встановлюємо змінні середовища
ENV PYTHONUNBUFFERED=1

# Місце, на якому працює Django
EXPOSE 8000

# Команда для запуску Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "comments.wsgi:application"]

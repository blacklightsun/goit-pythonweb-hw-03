FROM python:3.12.12-alpine3.22

# Встановимо змінну середовища
ENV SITE_HOME=/site

# Встановимо робочу директорію всередині контейнера
WORKDIR $SITE_HOME

# Define a volume for persistent data
VOLUME ["$SITE_HOME/statics/storage"]

# ---- Оптимізація та Встановлення Залежностей ----

# 1. Скопіюємо ТІЛЬКИ файл із залежностями
# Це дозволить Docker кешувати шар зі встановленими бібліотеками
COPY requirements.txt .

# 2. Встановимо залежності
# --no-cache-dir гарантує, що кеш pip не буде збережено,
# що критично для зменшення розміру образу
RUN pip install -r requirements.txt --no-cache-dir

# 3. Тепер скопіюємо решту файлів проєкту в робочу директорію
COPY . .

# ---- Кінець змін ----

# дозволимо всім користувачам читати і писати файл data.json
RUN chmod 666 statics/storage/data.json

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 3000

# Запустимо наш застосунок всередині контейнера
ENTRYPOINT ["python", "main.py"]
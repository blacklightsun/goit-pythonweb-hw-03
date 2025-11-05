FROM python:3.12.12-alpine3.22

# Встановимо змінну середовища
ENV SITE_HOME=/site

# Встановимо робочу директорію всередині контейнера
WORKDIR $SITE_HOME

# Define a volume for persistent data
VOLUME ["$SITE_HOME/statics/storage"]

# Скопіюємо інші файли в робочу директорію контейнера
COPY . .

# дозволимо всім користувачам читати і писати файл data.json
RUN chmod 666 statics/storage/data.json

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 3000

# Запустимо наш застосунок всередині контейнера
ENTRYPOINT ["python", "main.py"]


FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app


# Копируем только необходимые файлы
COPY requirements.txt ./
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y postgresql-client ca-certificates tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .

# Если порт не нужен для webhook, EXPOSE можно не указывать
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Moscow

# Запуск main.py
CMD ["python", "main.py"]
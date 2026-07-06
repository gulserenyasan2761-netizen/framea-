FROM python:3.9-slim

# Chrome ve Selenium bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Render'da kullandığımız komut burada da iş görür
CMD ["python", "bot.py"]

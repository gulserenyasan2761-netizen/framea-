import time
import os
import json
import sys
from flask import Flask
from groq import Groq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from threading import Thread

# Ayarlar
VIDEO_ID = "5jka-H-Hvy4"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

def get_driver():
    print("DEBUG: Driver başlatılıyor...", flush=True)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
    
    # Cookie Yükleme
    if os.path.exists('cookies.json'):
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except: continue
        driver.refresh()
        print("DEBUG: Cookies yüklendi.", flush=True)
    else:
        print("DEBUG: HATA: cookies.json bulunamadı!", flush=True)
        
    time.sleep(10)
    return driver

def bot_loop():
    print("🚀 Bot döngüsü başlatılıyor...", flush=True)
    try:
        driver = get_driver()
        print("✅ Driver başarılı.", flush=True)
        
        # İlk mesaj denemesi
        try:
            chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
            chat_box.send_keys("Bot aktif edildi!")
            chat_box.send_keys(Keys.ENTER)
            print("✅ Başlangıç mesajı gönderildi!", flush=True)
        except Exception as e:
            print(f"❌ Input alanı bulunamadı: {e}", flush=True)

        # Mesaj dinleme döngüsü
        while True:
            elements = driver.find_elements(By.CSS_SELECTOR, "#message")
            if elements:
                son = elements[-1].text
                print(f"💬 Son mesaj: {son}", flush=True)
            time.sleep(15) 
            
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}", flush=True)

@app.route('/')
def home():
    return "FrameAI Bot 7/24 Aktif!"

# Flask ve Botu Başlat
if __name__ == "__main__":
    print("DEBUG: Thread ve Flask başlatılıyor...", flush=True)
    t = Thread(target=bot_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

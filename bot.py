import pytchat
import json
import time
import os
from flask import Flask
from groq import Groq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from threading import Thread

# --- AYARLAR ---
VIDEO_ID = "5jka-H-Hvy4"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

@app.route('/')
def home():
    return "FrameAI Bot 7/24 Aktif!"

def send_youtube_message(message):
    options = Options()
    options.add_argument("--headless") # Arka planda çalışması için
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
        
        # Cookie'leri yükle
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        
        driver.refresh()
        time.sleep(5) # Sayfanın yüklenmesini bekle
        
        # Mesaj kutusunu bul ve yaz
        # Not: YouTube chat kutusu class ismi değişebilir, "input" veya "textarea" en garantisidir
        chat_box = driver.find_element(By.ID, "input") 
        chat_box.send_keys(message)
        chat_box.send_keys(Keys.ENTER)
        print(f"✅ Mesaj gönderildi: {message}")
    except Exception as e:
        print(f"❌ Mesaj gönderme hatası: {e}")
    finally:
        driver.quit()

def bot_listener():
    chat = pytchat.create(video_id=VIDEO_ID)
    print("🚀 Bot dinlemeye başladı...")
    
    while chat.is_alive():
        for c in chat.get().sync_items():
            if "!bot" in c.message.lower():
                soru = c.message.replace("!bot", "").strip()
                print(f"🤖 Soru alındı: {soru}")
                
                # AI Cevabı
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": soru}],
                    model="llama-3.1-8b-instant"
                )
                cevap = completion.choices[0].message.content
                
                # Cevabı Gönder
                send_youtube_message(f"@ {c.author.name} {cevap[:150]}") # 150 karakter sınırı

if __name__ == "__main__":
    Thread(target=bot_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

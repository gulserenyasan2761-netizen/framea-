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
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
app = Flask(__name__)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument("--no-zygote")
    # Railway'deki Chromium yolu:
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
    
    # Cookie yükleme
    if os.path.exists('cookies.json'):
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                try: driver.add_cookie(cookie)
                except: continue
        driver.refresh()
        print("🍪 Cookies yüklendi.", flush=True)
    return driver

def bot_loop():
    print("🚀 Bot döngüsü başlatılıyor...", flush=True)
    try:
        driver = get_driver()
        print("✅ Driver hazır.", flush=True)
        
        last_promotion_time = time.time()
        last_msg_id = ""

        while True:
            # 10 dakikada bir tanıtım mesajı
            if time.time() - last_promotion_time > 600:
                try:
                    chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
                    chat_box.send_keys("Selam! Ben DiamondPickaxe AI. !bot ile bana soru sorabilirsiniz.")
                    chat_box.send_keys(Keys.ENTER)
                    print("📢 Tanıtım mesajı gönderildi!", flush=True)
                    last_promotion_time = time.time()
                except Exception as e:
                    print(f"⚠️ Tanıtım hatası: {e}", flush=True)

            # Mesaj kontrolü
            try:
                # En son mesajı bul
                messages = driver.find_elements(By.CSS_SELECTOR, "#message")
                if messages:
                    last_msg = messages[-1].text
                    # Yeni mesaj mı?
                    if "!bot" in last_msg.lower() and last_msg != last_msg_id:
                        last_msg_id = last_msg
                        soru = last_msg.replace("!bot", "").strip()
                        
                        # AI Yanıtı
                        completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": soru}],
                            model="llama-3.1-8b-instant"
                        )
                        cevap = completion.choices[0].message.content[:100]
                        
                        # Yanıtı gönder
                        chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
                        chat_box.send_keys(cevap)
                        chat_box.send_keys(Keys.ENTER)
                        print(f"✅ Cevap gönderildi: {cevap}", flush=True)
            except:
                pass
            
            time.sleep(5)
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}", flush=True)

@app.route('/')
def home():
    return "DiamondPickaxe AI - Railway Modu Aktif!"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

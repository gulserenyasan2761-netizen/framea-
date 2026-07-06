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
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
    
    if os.path.exists('cookies.json'):
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                try: driver.add_cookie(cookie)
                except: continue
        driver.refresh()
    return driver

def bot_loop():
    print("🚀 Bot döngüsü başlatılıyor...", flush=True)
    try:
        driver = get_driver()
        print("✅ Driver hazır.", flush=True)
        
        last_promotion_time = time.time() # Zamanlayıcıyı başlat

        while True:
            # 10 Dakikada bir tanıtım mesajı
            current_time = time.time()
            if current_time - last_promotion_time > 600: # 600 saniye = 10 dakika
                try:
                    chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
                    chat_box.send_keys("Selam! Ben DiamondPickaxe AI. !bot ile bana soru sorabilirsiniz.")
                    chat_box.send_keys(Keys.ENTER)
                    print("📢 Tanıtım mesajı gönderildi!", flush=True)
                    last_promotion_time = current_time
                except Exception as e:
                    print(f"⚠️ Tanıtım mesajı gönderilemedi: {e}", flush=True)

            # Mesaj kontrolü
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, "#message")
                if elements:
                    son = elements[-1].text
                    # Basit bir "son mesaj kontrolü" (sürekli aynı mesajı okumasın diye)
                    if "!bot" in son.lower() and not hasattr(bot_loop, "last_msg"):
                        bot_loop.last_msg = ""
                    
                    if "!bot" in son.lower() and son != getattr(bot_loop, "last_msg", ""):
                        bot_loop.last_msg = son
                        soru = son.replace("!bot", "").strip()
                        completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": soru}],
                            model="llama-3.1-8b-instant"
                        )
                        cevap = completion.choices[0].message.content[:100]
                        
                        chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
                        chat_box.send_keys(cevap)
                        chat_box.send_keys(Keys.ENTER)
                        print(f"✅ Cevap gönderildi: {cevap}", flush=True)
            except:
                pass
                
            time.sleep(5) # Döngü beklemesi
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}", flush=True)

@app.route('/')
def home():
    return "DiamondPickaxe AI Bot Aktif!"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

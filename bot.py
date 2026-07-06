import time
import os
import json
from flask import Flask
from groq import Groq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
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
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    
    # Railway ve Docker için otomatik driver kurulumu
    service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
    
    if os.path.exists('cookies.json'):
        with open('cookies.json', 'r') as f:
            try:
                cookies = json.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
                print("🍪 Cookies başarıyla yüklendi.", flush=True)
            except Exception as e:
                print(f"⚠️ Cookie yüklenirken hata: {e}", flush=True)
    return driver

def bot_loop():
    print("🚀 Bot döngüsü başlatılıyor...", flush=True)
    try:
        driver = get_driver()
        print("✅ Driver hazır, bot yayında!", flush=True)
        
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
                except: pass

            # Mesaj kontrolü
            try:
                messages = driver.find_elements(By.CSS_SELECTOR, "#message")
                if messages:
                    last_msg = messages[-1].text
                    if "!bot" in last_msg.lower() and last_msg != last_msg_id:
                        last_msg_id = last_msg
                        soru = last_msg.replace("!bot", "").strip()
                        
                        completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": soru}],
                            model="llama-3.1-8b-instant"
                        )
                        cevap = completion.choices[0].message.content[:100]
                        
                        chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
                        chat_box.send_keys(cevap)
                        chat_box.send_keys(Keys.ENTER)
                        print(f"✅ Cevap gönderildi: {cevap}", flush=True)
            except: pass
            time.sleep(5)
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}", flush=True)

@app.route('/')
def home():
    return "DiamondPickaxe AI - Bot Aktif ve Çalışıyor!"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    # Railway'in atadığı portu otomatik al
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

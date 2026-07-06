import time
import os
import json
from flask import Flask
from groq import Groq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from threading import Thread

VIDEO_ID = "5jka-H-Hvy4"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled") # BOT OLDUĞUNU GİZLE
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
        print("🍪 Cookies yüklendi ve sayfa yenilendi.")
    else:
        print("⚠️ HATA: cookies.json dosyası bulunamadı!")
        
    time.sleep(10)
    return driver

def bot_loop():
    print("🚀 Bot döngüsü başlatılıyor...")
    try:
        driver = get_driver()
        print("✅ Driver başarılı.")
        
        # Sayfayı kontrol et
        print(f"DEBUG: Sayfa başlığı: {driver.title}")
        
        # Chat giriş kutusunu bulmak için daha geniş bir seçici
        # Bazen 'input' bazen de 'input-container' kullanılır
        chat_box = None
        try:
            chat_box = driver.find_element(By.CSS_SELECTOR, "#input")
            chat_box.send_keys("Bot aktif edildi!")
            chat_box.send_keys(Keys.ENTER)
            print("✅ Başlangıç mesajı gönderildi!")
        except:
            print("❌ Input alanı bulunamadı! Sayfa içeriği: ", driver.page_source[:500])

        while True:
            elements = driver.find_elements(By.CSS_SELECTOR, "#message")
            if elements:
                son = elements[-1].text
                print(f"💬 Son görülen: {son}")
            time.sleep(15) # Çok sık sorgu atma, engellenirsin
            
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}")

@app.route('/')
def home():
    return "FrameAI Bot 7/24 Aktif!"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

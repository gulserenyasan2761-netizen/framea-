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
app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("user-data-dir=./ChromeBotProfile") 
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
    
    # Cookie'leri yükle
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(5)
    return driver

def bot_loop():
    driver = get_driver()
    print("🚀 Bot yayına giriş yaptı ve dinlemeye başladı...")
    
    while True:
        try:
            # Chat'teki mesajları oku
            messages = driver.find_elements(By.CSS_SELECTOR, "#message")
            if messages:
                son_mesaj = messages[-1].text
                if "!bot" in son_mesaj.lower():
                    soru = son_mesaj.replace("!bot", "").strip()
                    print(f"🤖 Soru: {soru}")
                    
                    # AI Cevabı
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": soru}],
                        model="llama-3.1-8b-instant"
                    )
                    cevap = completion.choices[0].message.content[:150]
                    
                    # Mesajı Yaz
                    chat_box = driver.find_element(By.ID, "input")
                    chat_box.send_keys(cevap)
                    chat_box.send_keys(Keys.ENTER)
                    print(f"✅ Gönderildi: {cevap}")
            
            time.sleep(10) # 10 saniyede bir kontrol et
        except Exception as e:
            print(f"Hata: {e}")
            driver.refresh()
            time.sleep(5)

@app.route('/')
def home():
    return "FrameAI Bot Çalışıyor!"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

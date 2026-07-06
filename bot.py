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

# AYARLAR
VIDEO_ID = "5jka-H-Hvy4"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.youtube.com/live_chat?v={VIDEO_ID}")
    
    # Cookie'leri yükle
    try:
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    continue
        driver.refresh()
        time.sleep(10) # Sayfanın oturumla yüklenmesi için bekle
    except Exception as e:
        print(f"Cookie hatası: {e}")
    return driver

def bot_loop():
    driver = get_driver()
    print("🚀 Bot yayına giriş yaptı, mesajlar dinleniyor...")
    send_message("Merhaba, ben DiamondPickaxe AI! Frame AI'ın kardeşiyim. Sorularınızı !bot yazarak sorabilirsiniz.")
    try:
        chat_box = driver.find_element(By.ID, "input")
        chat_box.send_keys("Bot aktif edildi!")
        chat_box.send_keys(Keys.ENTER)
        print("✅ Başlangıç mesajı gönderildi!")
    except Exception as e:
        print(f"⚠️ Başlangıç mesajı gönderilemedi: {e}")
    last_message = ""
    
    while True:
        try:
            # Chat mesajlarını bul
            elements = driver.find_elements(By.CSS_SELECTOR, "#message")
            if elements:
                current_message = elements[-1].text
                if current_message != last_message:
                    last_message = current_message
                    print(f"💬 Yeni mesaj: {current_message}")
                    
                    if "!bot" in current_message.lower():
                        soru = current_message.replace("!bot", "").strip()
                        print(f"🤖 İşleniyor: {soru}")
                        
                        completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": soru}],
                            model="llama-3.1-8b-instant"
                        )
                        cevap = completion.choices[0].message.content[:150]
                        
                        # Yazma alanı
                        chat_box = driver.find_element(By.ID, "input")
                        chat_box.send_keys(cevap)
                        chat_box.send_keys(Keys.ENTER)
                        print(f"✅ Gönderildi: {cevap}")
            
            time.sleep(5)
        except Exception as e:
            print(f"Döngü hatası: {e}")
            time.sleep(10)

@app.route('/')
def home():
    return "FrameAI Bot 7/24 Aktif!"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

import requests
import time

BOT_TOKEN = "8766725521:AAE2fEB8-2nu05ON026ILLV3-avcEp1q2fc"

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

print("🤖 Բոտը աշխատում է...")
last_update_id = None

while True:
    updates = get_updates(last_update_id)
    if updates.get("ok") and updates.get("result"):
        for update in updates["result"]:
            last_update_id = update["update_id"] + 1
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")
                if text == "/start":
                    send_message(chat_id, "✅ Բոտը աշխատում է!")
                elif text == "/ping":
                    send_message(chat_id, "🏓 Pong!")
                elif text.startswith("/send"):
                    parts = text.split(" ", 2)
                    if len(parts) >= 3:
                        send_message(chat_id, f"📤 Ուղարկված է: {parts[2]}")
                else:
                    send_message(chat_id, f"📌 Չճանաչված հրաման: {text}")
    time.sleep(1)

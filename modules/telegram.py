import requests

def send_telegram(message, config):
    token = config["telegram_bot_token"]
    chat_id = config["telegram_chat_id"]

    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=1)
    except:
        pass

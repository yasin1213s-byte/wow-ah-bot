import requests
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# آیتم‌ها با Item ID در WoW
ITEMS = {
    "Bismuth": 224036,
    "Ironclaw Ore": 224037,
    "Mycobloom": 224073,
    "Shoregrass": 224071,
    "Luredrop": 224072,
    "Flask of Tempered Aggression": 212283,
    "Algari Mana Potion": 212265,
    "Culminating Blasphemite": 213746,
}

REALM = "kazzak"
REGION = "eu"
DISCOUNT_THRESHOLD = 0.80  # زیر ۸۰٪ میانگین = اعلان

def get_item_data(item_id):
    url = f"https://undermine.exchange/api/{REGION}/{REALM}/{item_id}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

def main():
    alerts = []

    for name, item_id in ITEMS.items():
        data = get_item_data(item_id)
        if not data:
            continue

        market_value = data.get("marketValue", 0)
        min_buyout = data.get("minBuyout", 0)

        if market_value == 0 or min_buyout == 0:
            continue

        ratio = min_buyout / market_value

        if ratio < DISCOUNT_THRESHOLD:
            profit = market_value - min_buyout
            profit_after_fee = int(profit * 0.95)
            discount_pct = int((1 - ratio) * 100)

            alerts.append(
                f"🟢 <b>{name}</b>\n"
                f"💰 قیمت فعلی: {min_buyout:,}g\n"
                f"📊 میانگین بازار: {market_value:,}g\n"
                f"📉 تخفیف: {discount_pct}%\n"
                f"✅ سود خالص: ~{profit_after_fee:,}g"
            )

    if alerts:
        header = "🏛 <b>WoW AH - فرصت‌های خرید زیر قیمت</b>\n\n"
        send_telegram(header + "\n\n---\n\n".join(alerts))
    else:
        send_telegram("✅ WoW AH چک شد — فرصت خاصی پیدا نشد.")

if __name__ == "__main__":
    main()

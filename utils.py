import requests

API_KEY = "pDUAhKJaZZlSXnWtSberXS6PCwfiGP4D"
CRM_URL = "https://valentinkalinovski.retailcrm.ru"


def get_order_by_bot_code_or_phone(code):
    url = f"{CRM_URL}/api/v5/orders"
    headers = {"X-API-KEY": API_KEY}

    # Поиск по bot_code
    params_code = {
        "customFields[bot_code]": code,
        "limit": 1,
        "apiKey": API_KEY
    }
    r1 = requests.get(url, params=params_code, headers=headers)
    if r1.ok and r1.json().get("orders"):
        order = r1.json()["orders"][0]
        return {"id": order["id"], "number": order["number"]}

    # Поиск по номеру телефона
    params_phone = {
        "customer[phone]": code,
        "limit": 1,
        "apiKey": API_KEY
    }
    r2 = requests.get(url, params=params_phone, headers=headers)
    if r2.ok and r2.json().get("orders"):
        order = r2.json()["orders"][0]
        return {"id": order["id"], "number": order["number"]}

    return None


def get_status_text(order_id):
    return f"📦 Заказ {order_id}: В пути. Скоро будет у вас!"


def get_track_text(order_id):
    return f"🚚 Трек-номер: 1234567890
Проверить можно тут: https://www.cdek.ru/tracking?order_id=1234567890"


def get_orders(active=True):
    if active:
        return "📦 Активные заказы:
1. Заказ A123 от 01.06.2025 — В пути"
    else:
        return "📦 Прошлые заказы:
1. Заказ A100 от 05.05.2025 — Доставлен"


def save_review_to_crm(order_id, comment):
    print(f"💬 Сохраняем комментарий в CRM: {comment}")
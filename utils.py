import requests

API_KEY = "pDUAhKJaZZlSXnWtSberXS6PCwfiGP4D"
CRM_URL = "https://valentinkalinovski.retailcrm.ru"


def get_order_by_bot_code_or_phone(code):
    url = f"{CRM_URL}/api/v5/orders"
    headers = {"X-API-KEY": API_KEY}
    params_code = {"customFields[bot_code]": code, "limit": 1, "apiKey": API_KEY}
    r1 = requests.get(url, params=params_code, headers=headers)
    if r1.ok and r1.json().get("orders"):
        order = r1.json()["orders"][0]
        return {"id": order["id"], "number": order["number"]}
    params_phone = {"customer[phone]": code, "limit": 1, "apiKey": API_KEY}
    r2 = requests.get(url, params=params_phone, headers=headers)
    if r2.ok and r2.json().get("orders"):
        order = r2.json()["orders"][0]
        return {"id": order["id"], "number": order["number"]}
    return None


def get_status_text(order_id):
    return f"📦 Заказ {order_id}: В пути. Скоро будет у вас!"


def get_track_text(order_id):
    url = f"{CRM_URL}/api/v5/orders/{order_id}"
    headers = {"X-API-KEY": API_KEY}
    r = requests.get(url, headers=headers)
    if r.ok:
        order = r.json().get("order", {})
        track = order.get("delivery", {}).get("number")
        if track:
            return f"🚚 Трек-номер: {track}
Проверить можно тут: https://www.cdek.ru/tracking?order_id={track}"
        else:
            return "📭 Пока трек-номер ещё не присвоен — как только он появится, я сразу расскажу!"
    return "⚠️ Не удалось получить информацию о заказе. Попробуйте позже."


def get_orders(active=True):
    if active:
        return "📦 Активные заказы:
1. Заказ A123 от 01.06.2025 — В пути"
    else:
        return "📦 Прошлые заказы:
1. Заказ A100 от 05.05.2025 — Доставлен"


def save_review_to_crm(order_id, comment):
    print(f"💬 Сохраняем комментарий в CRM: {comment}")
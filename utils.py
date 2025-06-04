def get_order_by_bot_code_or_phone(code):
    if code == "0000":
        return {"id": 1, "number": "A123"}
    return None

def get_status_text(order_id):
    return f"📦 Заказ {order_id}: В пути. Скоро будет у вас!"

def get_track_text(order_id):
    return f"🚚 Трек-номер: 1234567890\nПроверить можно тут: https://www.cdek.ru/tracking?order_id=1234567890"

def get_orders(active=True):
    if active:
        return "📦 Активные заказы:\n1. Заказ A123 от 01.06.2025"
    else:
        return "📁 Завершённые заказы:\n1. Заказ Z789 от 20.05.2025"

def save_review_to_crm(order_id, text):
    with open("reviews.txt", "a") as f:
        f.write(f"{order_id}: {text}\n")
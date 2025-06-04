def save_user_auth(user_id: int, order_id: int):
    with open("user_auth.txt", "a") as f:
        f.write(f"{user_id},{order_id}\n")

def get_order_id_by_user_id(user_id: int):
    try:
        with open("user_auth.txt", "r") as f:
            for line in f:
                uid, oid = line.strip().split(",")
                if int(uid) == user_id:
                    return int(oid)
    except FileNotFoundError:
        return None
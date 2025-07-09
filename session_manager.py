import os
import json
import uuid
import time

from utils.extract_memory_ai import extract_memory_from_message

DB_FILE_PRIVATE = "db.json"
DB_FILE_GROUP = "dbgroup.json"
SESSION_TIMEOUT = 600

def load_db(is_group: bool) -> dict:
    path = DB_FILE_GROUP if is_group else DB_FILE_PRIVATE
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_db(db: dict, is_group: bool):
    path = DB_FILE_GROUP if is_group else DB_FILE_PRIVATE
    with open(path, "w") as f:
        json.dump(db, f, indent=2)

def get_session(user_id: int, *, is_group=False) -> list:
    db = load_db(is_group)
    key = str(user_id)
    if key in db:
        session = db[key]
        if time.time() - session["metadata"]["created_at"] > SESSION_TIMEOUT:
            session["history"] = []
            session["metadata"]["created_at"] = time.time()
            save_db(db, is_group)
        return session["history"]
    return []

def update_memory(user_id: int, message: str):
    memory_data = extract_memory_from_message(message)
    if not memory_data or not isinstance(memory_data, dict):
        return

    db = load_db(False) 
    key = str(user_id)

    if key not in db:
        db[key] = {
            "type": "private",
            "metadata": {
                "session_id": str(uuid.uuid4()),
                "created_at": time.time()
            },
            "memory": {},
            "history": []
        }

    if "memory" not in db[key] or not isinstance(db[key]["memory"], dict):
        db[key]["memory"] = {}

    for k, v in memory_data.items():
        if isinstance(k, str) and isinstance(v, (str, int, float, list, dict)):
            db[key]["memory"][k] = v

    save_db(db, False)

def update_session(
    user_id: int,
    prompt: str,
    response: str,
    *,
    is_group=False,
    username="",
    phonenumber="",
    sendername="",
    msgtype="",
    groupid=""
):
    db = load_db(is_group)
    key = str(user_id)

    if key not in db:
        metadata = {
            "session_id": str(uuid.uuid4()),
            "created_at": time.time()
        }

        if is_group:
            metadata.update({
                "sendername": sendername or f"user_{user_id}",
                "msgtype": msgtype or "group",
                "groupid": groupid or "",
                "phonenumber": phonenumber or ""
            })
        else:
            metadata.update({
                "username": username or f"user_{user_id}",
                "phonenumber": phonenumber or ""
            })

        db[key] = {
            "type": "group" if is_group else "private",
            "metadata": metadata,
            "memory": {} if not is_group else None,
            "history": []
        }

    # Reset jika timeout
    if time.time() - db[key]["metadata"]["created_at"] > SESSION_TIMEOUT:
        db[key]["history"] = []
        db[key]["metadata"]["created_at"] = time.time()

    db[key]["history"].append({"role": "user", "content": prompt})
    db[key]["history"].append({"role": "assistant", "content": response})
    save_db(db, is_group)

    if not is_group:
        update_memory(user_id, prompt)

def clear_session(user_id: int, *, is_group=False):
    db = load_db(is_group)
    key = str(user_id)
    if key in db:
        db[key]["history"] = []
        db[key]["metadata"]["created_at"] = time.time()
        save_db(db, is_group)
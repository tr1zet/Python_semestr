import os
from datetime import datetime


def log_action(user_id, action, details=""):
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/{user_id}.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}: {details}\n")


def get_user_logs(user_id, limit=50):
    log_file = f"logs/{user_id}.log"
    
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            logs = [line.strip() for line in lines[-limit:]]
        return logs
    else:
        return ["Нет записей в логе"]


def clear_user_logs(user_id):
    log_file = f"logs/{user_id}.log"
    
    if os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] logs_cleared: История очищена\n")
        return True
    return False
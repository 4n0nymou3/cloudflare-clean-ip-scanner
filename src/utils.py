import json
import os

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def save_json(file_path: str, data: dict):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def format_ip(ip: str, port: int) -> str:
    if ':' in ip:
        return f"[{ip}]:{port}"
    else:
        return f"{ip}:{port}"

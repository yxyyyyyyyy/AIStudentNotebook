import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".xiaozhi_mcp_config.json"

def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "MCP_ENDPOINT": "wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjE2OTg0MywiYWdlbnRJZCI6MzQ5NDgxLCJlbmRwb2ludElkIjoiYWdlbnRfMzQ5NDgxIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc0OTM3MjEyMn0.u4PS_xHqTSqzR6Fd8L-yT8CPbBo3UbLYF-FYd_ghznr_NVJBtAJeQkn5UtJik-z822Gf_XLkatXAbrU8Qq_TEg",
            "ZHIPU_API_KEY": "064217d6930e42f3a57a28d966b5879c.G2QyMvMwXGTdxNoA",
        }

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
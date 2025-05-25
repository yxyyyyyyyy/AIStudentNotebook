from mcp.server.fastmcp import FastMCP
import logging
import json
import os
from datetime import datetime
import sys
import io
import requests

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    encoding="utf-8",
)
logger = logging.getLogger("memo_mcp")

mcp = FastMCP("Memo")

MEMO_FILE = "memos.json"

def notify_fastapi():
    try:
        res = requests.post("http://localhost:8000/memo/notify_update")
        if res.status_code == 200:
            logger.info("通知FastAPI更新成功")
        else:
            logger.warning(f"通知FastAPI更新失败，状态码：{res.status_code}")
    except Exception as e:
        logger.error(f"通知FastAPI更新异常: {e}")

def load_memos():
    if not os.path.exists(MEMO_FILE):
        return []
    try:
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载备忘录文件失败: {e}")
        return []

def save_memos(memos):
    try:
        with open(MEMO_FILE, "w", encoding="utf-8") as f:
            json.dump(memos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存备忘录文件失败: {e}")

@mcp.tool()
def add_memo(content: str) -> dict:
    logger.info(f"add_memo called with content: {content}")
    memos = load_memos()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memos.append({"content": content, "time": timestamp})
    save_memos(memos)
    notify_fastapi()  # 通知FastAPI
    return {"success": True, "message": f"已添加备忘：{content}"}

@mcp.tool()
def list_memos() -> dict:
    logger.info("list_memos called")
    memos = load_memos()
    if not memos:
        return {"success": True, "memos": "当前没有备忘内容。"}
    return {
        "success": True,
        "memos": "\n".join([f"{i+1}. {m['time']} - {m['content']}" for i, m in enumerate(memos)])
    }

@mcp.tool()
def delete_memo(keyword: str) -> dict:
    logger.info(f"delete_memo called with keyword: {keyword}")
    memos = load_memos()
    updated = [m for m in memos if keyword not in m["content"]]
    if len(updated) == len(memos):
        return {"success": False, "message": f"没有找到包含“{keyword}”的备忘。"}
    save_memos(updated)
    return {"success": True, "message": f"已删除包含“{keyword}”的备忘。"}

@mcp.tool()
def edit_memo(original: str, updated: str) -> dict:
    logger.info(f"edit_memo called with original: {original}, updated: {updated}")
    memos = load_memos()
    found = False
    for m in memos:
        if original in m["content"]:
            m["content"] = updated
            found = True
            break
    if not found:
        return {"success": False, "message": f"未找到包含“{original}”的备忘。"}
    save_memos(memos)
    return {"success": True, "message": f"已将“{original}”修改为“{updated}”。"}

@mcp.tool()
def clear_memos() -> dict:
    logger.info("clear_memos called")
    save_memos([])
    return {"success": True, "message": "所有备忘已清空。"}

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
        sys.stdout.flush()
    except UnicodeEncodeError:
        print("[UnicodeEncodeError in print]", flush=True)

if __name__ == "__main__":
    safe_print("MCP Memo backend starting...")
    mcp.run(transport="stdio")

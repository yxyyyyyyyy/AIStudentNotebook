from mcp.server.fastmcp import FastMCP
import logging
import json
import os
from datetime import datetime
import sys
import io
import sys
import platform
import subprocess


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

def load_memos():
    if not os.path.exists(MEMO_FILE):
        return []
    try:
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            memos = json.load(f)
        return memos
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
    logger.info(f"Added memo: {content}")
    return {"success": True, "message": f"已添加备忘：{content}"}

@mcp.tool()
def list_memos() -> dict:
    logger.info("list_memos called")
    memos = load_memos()
    if not memos:
        return {"success": True, "memos": "当前没有备忘内容。"}
    return {
        "success": True,
        "memos": "\n".join([f"{m['time']} - {m['content']}" for m in memos])
    }

@mcp.tool()
def clear_memos() -> dict:
    logger.info("clear_memos called")
    save_memos([])
    logger.info("Cleared all memos.")
    return {"success": True, "message": "所有备忘已清空。"}

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
        sys.stdout.flush()
    except UnicodeEncodeError:
        print("[UnicodeEncodeError in print]", flush=True)

@mcp.tool()
def shutdown_computer() -> dict:
    logger.info("shutdown_computer called")
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        elif system == "Linux" or system == "Darwin":  # Darwin 是 macOS
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        else:
            return {"success": False, "message": f"不支持的系统: {system}"}
        return {"success": True, "message": "电脑正在关机..."}
    except Exception as e:
        logger.error(f"关机失败: {e}")
        return {"success": False, "message": f"关机失败: {e}"}
        
if __name__ == "__main__":
    safe_print("MCP Memo backend starting...")
    mcp.run(transport="stdio")

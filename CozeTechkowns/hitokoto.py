import logging
import requests
from mcp.server.fastmcp import FastMCP
import sys
import io

# 编码处理
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 日志设置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    encoding="utf-8",
)
logger = logging.getLogger("hitokoto")

# MCP 初始化
mcp = FastMCP("Hitokoto")

@mcp.tool()
def ask_coze_bot(content: str) -> dict:
    """
    向 Coze 智能体提问并获取回复。
    关键词：coze 提问 

    参数:
    - content: 用户提出的问题内容

    返回:
    - 包含 Coze 智能体的回复内容
    """
    try:
        if not content.strip():
            return {"success": False, "message": "请输入有效的问题。"}

        url = "https://api.coze.cn/v3/chat"

        headers = {
            "Authorization": "pat_HuBOMiBbObhQAID8wMxTRV08BuaNkNpGA3UnkpwGR4FdG6lxafMaUJzIiIHLOGS9",  # ⚠️ 请替换为你的真实 pat_xxx 访问密钥
            "Content-Type": "application/json"
        }

        payload = {
            "bot_id": "7513017678085537804",  # ✅ 你的 Coze Bot ID
            "user_id": "123456",              # 可改为用户ID或用户session ID
            "stream": False,
            "auto_save_history": True,
            "additional_messages": [
                {
                    "role": "user",
                    "content": content,
                    "content_type": "text"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # 提取 assistant 回复内容
        reply = ""
        for msg in data.get("messages", []):
            if msg.get("role") == "assistant":
                reply = msg.get("content", "")
                break

        return {
            "success": True,
            "question": content,
            "answer": reply or "未获取到回答"
        }

    except Exception as e:
        logger.error(f"Coze 智能体请求失败: {e}")
        return {"success": False, "message": "请求失败"}


if __name__ == "__main__":
    print("Hitokoto MCP backend started.")
    mcp.run(transport="stdio")

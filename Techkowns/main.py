import logging
import requests
from mcp.server.fastmcp import FastMCP
import sys
import io

# 终端编码设置，避免中文乱码
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    encoding="utf-8",
)
logger = logging.getLogger("LocalVectorKB")
# MCP 初始化
mcp = FastMCP("Hitokoto")
import requests

@mcp.tool()
def query_vector_db(question: str, top_k: int = 1, min_score: float = 0.3) -> dict:
    """
    当用户问起小说里面的台词的时候调用这个接口
    输入：小说台词，小说经典台词，台词等
    参数：
        question: 查询问题文本
        top_k: 返回最相似的前几条结果（默认1）
        min_score: 过滤结果的相似度阈值（默认0.3）
    """
    try:
        resp = requests.get(
            "http://localhost:8000/search_v2",
            params={"question": question, "top_k": top_k, "min_score": min_score}
        )
        return resp.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
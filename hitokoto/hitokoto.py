# 获取一条随机一言。
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

# 类型映射字典
CATE_MAP = {
    "a": "动画",
    "b": "漫画",
    "c": "游戏",
    "d": "小说",
    "e": "原创",
    "f": "网络",
    "g": "其他",
    "h": "影视",
    "i": "诗词",
    "j": "网易云",
    "k": "哲学",
    "l": "抖机灵"
}

@mcp.tool()
def get_hitokoto(cate: str = None) -> dict:
    """
    获取一条随机一言。
    参数:
    - cate: 一言类型，可选值:
      a(动画), b(漫画), c(游戏), d(小说), e(原创), f(网络),
      g(其他), h(影视), i(诗词), j(网易云), k(哲学), l(抖机灵)
    返回:
    - 包含一言内容、来源等信息的字典
    """
    try:
        params = {}
        if cate:
            if cate not in CATE_MAP:
                return {"success": False, "message": "不支持的类型代号，请输入 a-l 之间的字母。"}
            params["c"] = cate

        response = requests.get("https://v1.hitokoto.cn", params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "hitokoto": data.get("hitokoto", ""),
            "from": data.get("from", ""),
            "creator": data.get("creator", ""),
            "type": CATE_MAP.get(data.get("type", ""), "未知")
        }
    except Exception as e:
        logger.error(f"获取一言失败: {e}")
        return {"success": False, "message": "获取一言失败"}

if __name__ == "__main__":
    print("Hitokoto MCP backend started.")
    mcp.run(transport="stdio")

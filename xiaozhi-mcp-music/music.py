from mcp.server.fastmcp import FastMCP
import requests
from playsound import playsound
import tempfile
import os
import logging
import threading

# 初始化MCP和日志
mcp = FastMCP("MusicPlayer")
logger = logging.getLogger(__name__)
_LOCK = threading.Lock()  # 保留原线程锁

_API_URL = 'https://api.yaohud.cn/api/music/wy'# 进网站去注册拿到API_KEY
_API_KEY = 'gKdP4sECc4NbbVxz868' # 此处填写自己的API_KEY

@mcp.tool()
def play_music(song_name: str) -> str:
    """
    通过MCP接口播放音乐（线程安全）
    Args:
        song_name: 歌曲名，默认为"好运来"
    Returns:
        str: 播放结果或错误信息
    """
    if not song_name.strip():
        return "错误：歌曲名不能为空"

    with _LOCK:
        try:
            # 1. 调用API获取音乐URL
            logger.info(f"搜索歌曲: {song_name}")
            params = {'key': _API_KEY, 'msg': song_name.strip(), 'n': '1'}
            resp = requests.post(_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            music_url = resp.json()['data']['musicurl']

            # 2. 下载并保存临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(requests.get(music_url, timeout=10).content)
                temp_path = f.name

            # 3. 播放并返回结果
            playsound(temp_path)
            os.unlink(temp_path)  # 立即清理
            return f"播放成功: {song_name}"

        except Exception as e:
            logger.error(f"播放失败: {str(e)}")
            return f"播放失败: {str(e)}"
s
if __name__ == "__main__":
    mcp.run(transport="stdio")  # MCP标准输入输出模式

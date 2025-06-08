from mcp.server.fastmcp import FastMCP
import requests
import tempfile
import os
import logging
import threading
import pygame  # 替代 playsound

# 初始化 MCP 和日志
mcp = FastMCP("MusicPlayer")
logger = logging.getLogger(__name__)
_LOCK = threading.Lock()
    
# 初始化 pygame 音频模块
pygame.mixer.init()

_API_URL = 'https://api.yaohud.cn/api/music/wy'
_API_KEY = 'gKdP4sECc4NbbVxz868'


@mcp.tool()
def play_music(song_name: str) -> str:
    """
    关键字:我想听
    播放歌曲先用这个方法进行搜索
    通过 MCP 接口播放音乐（线程安全）
    Args:
        song_name: 歌曲名
    Returns:
        str: 播放结果或错误信息
    """
    if not song_name.strip():
        return "错误：歌曲名不能为空"
    with _LOCK:
        try:
            # 1. 调用 API 获取音乐 URL
            logger.info(f"搜索歌曲: {song_name}")
            params = {'key': _API_KEY, 'msg': song_name.strip(), 'n': '1'}
            resp = requests.post(_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            music_url = resp.json()['data']['musicurl']

            # 2. 下载 mp3 到临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(requests.get(music_url, timeout=10).content)
                temp_path = f.name

            # 3. 使用 pygame 播放
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            # 等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            os.unlink(temp_path)  # 删除临时文件
            return f"播放成功: {song_name}"

        except Exception as e:
            logger.error(f"播放失败: {str(e)}")
            return f"播放失败: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
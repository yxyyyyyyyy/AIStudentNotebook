from mcp.server.fastmcp import FastMCP
import requests
import tempfile
import os
import logging
import threading
import pygame  

# 初始化 MCP 和日志
mcp = FastMCP("MusicPlayer")
logger = logging.getLogger(__name__)
_LOCK = threading.Lock()
    
# 初始化 pygame 音频模块
pygame.mixer.init()

# 实现本地播放音乐,不过是从电脑端输出的音乐
_API_URL = 'https://api.yaohud.cn/api/music/wy'
_API_KEY = 'gKdP4sECc4NbbVxz868'


def _play_music_thread(temp_path: str):
    try:
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        logger.error(f"播放线程错误: {e}")
    finally:
        os.unlink(temp_path)  # 播放完成后删除临时文件

@mcp.tool()
def 播放音乐(song_name: str) -> str:
    """
    通过MCP接口播放音乐（线程安全）
    Args:
        song_name: 歌曲名，默认为"好运来"
    Returns:
        str: 播放结果或错误信息
    """
    logger.info(f"播放歌曲: {song_name}")
    if not song_name.strip():
        return "错误：歌曲名不能为空"
    with _LOCK:
        try:
            # 获取音乐链接
            logger.info(f"搜索歌曲: {song_name}")
            params = {'key': _API_KEY, 'msg': song_name.strip(), 'n': '1'}
            resp = requests.post(_API_URL, params=params, timeout=10)
            resp.raise_for_status()
            music_url = resp.json()['data']['musicurl']

            # 下载音乐
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(requests.get(music_url, timeout=10).content)
                temp_path = f.name

            # 使用线程播放音乐
            threading.Thread(target=_play_music_thread, args=(temp_path,), daemon=True).start()

            return f"正在播放: {song_name}"

        except Exception as e:
            logger.error(f"播放失败: {str(e)}")
            return f"播放失败: {str(e)}"


if __name__ == "__main__":
    logger.info("正在启动音乐播放服务")
    mcp.run(transport="stdio")
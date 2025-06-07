from mcp.server.fastmcp import FastMCP
import logging
import json
import os
from datetime import datetime
import sys
import io
import sys
import webbrowser
import subprocess
import platform
import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    encoding="utf-8",
)
logger = logging.getLogger("computer_control")

mcp = FastMCP("Computer")

LAST_URL_FILE = "last_url.txt"
LAST_VIDEO_FILE = "last_video.txt"

# 打开网页并记录
@mcp.tool()
def open_webpage(url: str) -> dict:
    logger.info(f"open_webpage called with URL: {url}")
    try:
        webbrowser.open(url)
        with open(LAST_URL_FILE, "w", encoding="utf-8") as f:
            f.write(url)
        return {"success": True, "message": f"已打开网页：{url}"}
    except Exception as e:
        logger.error(f"打开网页失败: {e}")
        return {"success": False, "message": "打开网页失败。"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_VIDEO_FILE = os.path.join(BASE_DIR, "last_video.txt")
LAST_SEARCH_FILE = os.path.join(BASE_DIR, "last_search.txt")
@mcp.tool()
def search_in_webpage(url: str, keyword: str) -> dict:
    """
    打开网页并在其中执行搜索（自动识别搜索框并输入关键词）。
    """
    logger.info(f"search_in_webpage called with URL: {url}, keyword: {keyword}")
    try:
        options = Options()
        options.add_argument("--start-maximized")
        # 可选：无头模式（不显示窗口）
        # options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2)  # 等待网页加载完成

        # 查找搜索框：先尝试 <input type="search">，再尝试 <input type="text">
        try:
            search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
        except:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            except:
                logger.warning("未找到可用的搜索输入框。")
                return {"success": False, "message": "未在网页中找到搜索框。"}

        # 输入关键词并回车
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        with open(LAST_SEARCH_FILE, "w", encoding="utf-8") as f:
            f.write(f"{url} 搜索：{keyword}")

        return {"success": True, "message": f"已在网页中搜索：{keyword}"}

    except Exception as e:
        logger.error(f"网页搜索失败: {e}")
        return {"success": False, "message": "网页搜索失败。"}
    
@mcp.tool()
def remember_last_video(title: str, url: str) -> dict:
    try:
        with open(LAST_VIDEO_FILE, "w", encoding="utf-8") as f:
            f.write(f"{title.strip()}\n{url.strip()}\n")
        return {"success": True, "message": f"已记录视频：{title}"}
    except Exception as e:
        return {"success": False, "message": f"记录视频失败: {e}"}

@mcp.tool()
def open_last_video_link() -> dict:
    if not os.path.exists(LAST_VIDEO_FILE):
        return {"success": False, "message": "没有记录任何视频链接。"}
    try:
        with open(LAST_VIDEO_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 2:
                return {"success": False, "message": "视频记录格式错误。"}
            title = lines[0].strip()
            url = lines[1].strip()
            webbrowser.open(url)
            return {"success": True, "message": f"正在打开：{title or url}"}
    except Exception as e:
        return {"success": False, "message": f"打开视频链接失败: {e}"}
def find_wechat_path() -> str:
    candidates = [
        r"C:\Program Files\Tencent\WeChat\WeChat.exe",
        r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""

@mcp.tool()
def open_wechat() -> dict:
    logger.info("open_wechat called")
    try:
        if platform.system() == "Windows":
            wechat_path = find_wechat_path()
            if not os.path.exists(wechat_path):
                return {"success": False, "message": f"未找到微信路径：{wechat_path}"}
            subprocess.Popen([wechat_path])
        else:
            subprocess.Popen(["wechat"])
        return {"success": True, "message": "正在打开微信..."}
    except Exception as e:
        logger.error(f"打开微信失败: {e}")
        return {"success": False, "message": "打开微信失败。"}


@mcp.tool()
def open_last_video_link() -> dict:
    logger.info("open_last_video_link called")
    if not os.path.exists(LAST_VIDEO_TXT):
        return {"success": False, "message": "没有记录任何视频链接。"}
    try:
        with open(LAST_VIDEO_TXT, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) < 2:
                return {"success": False, "message": "视频记录格式错误。"}
            title = lines[0].strip()
            link = lines[1].strip()
            webbrowser.open(link)
            return {
                "success": True,
                "message": f"正在打开：{title or link}"
            }
    except Exception as e:
        logger.error(f"读取或打开 last_video.txt 失败: {e}")
        return {
            "success": False,
            "message": "打开视频链接失败。"
        }

# 电脑休眠
@mcp.tool()
def sleep_computer() -> dict:
    logger.info("sleep_computer called")
    try:
        if platform.system() == "Windows":
            subprocess.call("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call("pmset sleepnow", shell=True)
        elif platform.system() == "Linux":
            subprocess.call("systemctl suspend", shell=True)
        else:
            return {"success": False, "message": "不支持的操作系统。"}
        return {"success": True, "message": "电脑即将休眠..."}
    except Exception as e:
        logger.error(f"休眠失败: {e}")
        return {"success": False, "message": "电脑休眠失败。"}

if __name__ == "__main__":
    mcp.run(transport="stdio")

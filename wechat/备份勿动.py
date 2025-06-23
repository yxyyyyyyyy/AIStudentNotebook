import logging
import subprocess
import time
import sys
import io
import os
from mcp.server.fastmcp import FastMCP

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
logger = logging.getLogger("wechat_control_advanced")

# MCP 初始化
mcp = FastMCP("WeChat Control Advanced")

# 微信相关常量
WECHAT_PROCESS_NAME = "WeChat.exe"
WECHAT_APP_NAME = "微信"
MOMENTS_ICON_PATH = "resources/icons/wechat_moments_icon.png"  # 朋友圈图标截图路径

# 依赖检测
def check_dependencies():
    missing = []
    available = {}
    try:
        import win32gui
        import win32con
        available['win32gui'] = True
    except ImportError:
        missing.append('pywin32')
        available['win32gui'] = False
    try:
        import pyautogui
        available['pyautogui'] = True
    except ImportError:
        missing.append('pyautogui')
        available['pyautogui'] = False
    try:
        import pyperclip
        available['pyperclip'] = True
    except ImportError:
        missing.append('pyperclip')
        available['pyperclip'] = False
    try:
        import pytesseract
        from PIL import ImageGrab
        available['ocr'] = True
    except ImportError:
        missing.append('pytesseract pillow')
        available['ocr'] = False

    return {
        'available': available,
        'missing': missing,
        'all_available': len(missing) == 0
    }

# 子进程执行
def safe_subprocess_run(cmd, **kwargs):
    try:
        result = subprocess.run(cmd, capture_output=True, **kwargs)
        encodings = ['utf-8', 'gbk', 'gb2312', 'cp936']
        stdout = stderr = ""
        for enc in encodings:
            try:
                stdout = result.stdout.decode(enc)
                stderr = result.stderr.decode(enc)
                break
            except:
                continue
        return type('SafeResult', (), {
            "returncode": result.returncode,
            "stdout": stdout or result.stdout.decode(errors='ignore'),
            "stderr": stderr or result.stderr.decode(errors='ignore')
        })()
    except Exception as e:
        logger.error(f"subprocess运行失败: {e}")
        raise

def find_wechat_path():
    paths = [
        os.path.expanduser("~/AppData/Local/Tencent/WeChat/WeChat.exe"),
        "C:/Program Files (x86)/Tencent/WeChat/WeChat.exe",
        "C:/Program Files/Tencent/WeChat/WeChat.exe",
        "D:/Program Files (x86)/Tencent/WeChat/WeChat.exe",
        "D:/Program Files/Tencent/WeChat/WeChat.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def find_wechat_window_advanced():
    try:
        import win32gui
        import win32con
        windows = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if any(k in text.lower() for k in ['微信', 'wechat']):
                    rect = win32gui.GetWindowRect(hwnd)
                    windows.append({
                        'hwnd': hwnd, 'title': text, 'rect': rect,
                        'width': rect[2]-rect[0], 'height': rect[3]-rect[1]
                    })
        win32gui.EnumWindows(callback, windows)
        windows.sort(key=lambda w: w['width'] * w['height'], reverse=True)
        return windows
    except:
        return []

def activate_wechat_window():
    try:
        import win32gui
        import win32con
        import pyautogui
        windows = find_wechat_window_advanced()
        if windows:
            hwnd = windows[0]['hwnd']
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            return True
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        return True
    except:
        return False

# 图像识别点击
def find_and_click_image(template_path, confidence=0.85):
    import pyautogui
    if not os.path.exists(template_path):
        return False
    location = pyautogui.locateCenterOnScreen(template_path, confidence=confidence, grayscale=True)
    if location:
        pyautogui.moveTo(location)
        pyautogui.click()
        return True
    return False

# OCR 检测
def ocr_window_text(region=None):
    from PIL import ImageGrab
    import pytesseract
    img = ImageGrab.grab(bbox=region) if region else ImageGrab.grab()
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    return text.strip()

@mcp.tool()
def open_wechat_moments() -> dict:
    try:
        if not open_wechat()["success"]:
            return {"success": False, "message": "微信未成功打开"}
        if not activate_wechat_window():
            return {"success": False, "message": "激活窗口失败"}

        time.sleep(2)
        if find_and_click_image(MOMENTS_ICON_PATH):
            time.sleep(2)
            text = ocr_window_text()
            return {"success": True, "message": f"已点击朋友圈图标，当前OCR页面识别：{text}"}
        return {"success": False, "message": "未找到朋友圈图标"}
    except Exception as e:
        return {"success": False, "message": f"打开朋友圈失败: {e}"}

@mcp.tool()
def open_wechat() -> dict:
    try:
        result = safe_subprocess_run(['tasklist', '/FI', f'IMAGENAME eq {WECHAT_PROCESS_NAME}'])
        if WECHAT_PROCESS_NAME in result.stdout:
            return {"success": True, "message": "微信已在运行"}
        path = find_wechat_path()
        if path:
            subprocess.Popen([path])
        else:
            subprocess.Popen(['start', WECHAT_APP_NAME], shell=True)
        time.sleep(5)
        return {"success": True, "message": "已尝试启动微信"}
    except Exception as e:
        return {"success": False, "message": f"启动微信失败: {e}"}

@mcp.tool()
def send_wechat_message(contact_name: str, message: str) -> dict:
    try:
        import pyautogui, pyperclip
        result = open_wechat_chat(contact_name)
        if not result["success"]:
            return result

        time.sleep(1.5)  # 等聊天框稳定后再粘贴

        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')

        return {
            "success": True,
            "message": f"已向“{contact_name}”发送消息：{message}"
        }
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return {"success": False, "message": f"发送消息失败: {str(e)}"}


@mcp.tool()
def open_wechat_chat(contact_name: str) -> dict:
    try:
        import pyautogui, pyperclip
        if not open_wechat()["success"]:
            return {"success": False, "message": "微信未运行"}
        if not activate_wechat_window():
            return {"success": False, "message": "无法激活微信窗口"}

        time.sleep(1)

        # 打开搜索框
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.8)

        # 粘贴联系人名
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.2)

        # 第一次回车选中高亮项
        pyautogui.press('enter')
        time.sleep(0.8)

        # 再次回车以进入聊天框
        pyautogui.press('enter')
        time.sleep(0.8)

        return {"success": True, "message": f"已尝试进入联系人“{contact_name}”的聊天窗口"}

    except Exception as e:
        logger.error(f"打开联系人对话框失败: {e}")
        return {"success": False, "message": f"打开联系人对话框失败: {str(e)}"}

if __name__ == "__main__":
    print("✅ WeChat Control (Advanced) 启动成功")
    deps = check_dependencies()
    if not deps['all_available']:
        print("❌ 缺少依赖：", ", ".join(deps['missing']))
        print("建议运行：pip install " + " ".join(deps['missing']))
    else:
        print("✅ 所有依赖已安装")
    mcp.run(transport="stdio")

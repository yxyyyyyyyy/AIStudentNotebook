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
logger = logging.getLogger("wechat_control_simple")

# MCP 初始化
mcp = FastMCP("WeChat Control Simple")

# 微信相关常量
WECHAT_PROCESS_NAME = "WeChat.exe"
WECHAT_APP_NAME = "微信"

def safe_subprocess_run(cmd, **kwargs):
    """安全运行subprocess命令，处理编码问题"""
    try:
        result = subprocess.run(cmd, capture_output=True, **kwargs)
        encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin1']
        stdout = ""
        stderr = ""
        
        for encoding in encodings:
            try:
                stdout = result.stdout.decode(encoding)
                stderr = result.stderr.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if not stdout:
            stdout = result.stdout.decode('utf-8', errors='ignore')
        if not stderr:
            stderr = result.stderr.decode('utf-8', errors='ignore')
        
        class SafeResult:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        
        return SafeResult(result.returncode, stdout, stderr)
    except Exception as e:
        logger.error(f"subprocess运行失败: {e}")
        raise

def find_wechat_path():
    """查找微信安装路径"""
    possible_paths = [
        os.path.expanduser("~/AppData/Local/Tencent/WeChat/WeChat.exe"),
        "C:/Program Files (x86)/Tencent/WeChat/WeChat.exe",
        "C:/Program Files/Tencent/WeChat/WeChat.exe",
        "D:/Program Files (x86)/Tencent/WeChat/WeChat.exe",
        "D:/Program Files/Tencent/WeChat/WeChat.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def check_dependencies():
    """检查必要的依赖库"""
    missing = []
    available = {}
    
    # 检查pywin32
    try:
        import win32gui
        import win32con
        available['win32gui'] = True
    except ImportError:
        missing.append('pywin32')
        available['win32gui'] = False
    
    # 检查pyautogui
    try:
        import pyautogui
        available['pyautogui'] = True
    except ImportError:
        missing.append('pyautogui')
        available['pyautogui'] = False
    
    # 检查pyperclip
    try:
        import pyperclip
        available['pyperclip'] = True
    except ImportError:
        missing.append('pyperclip')
        available['pyperclip'] = False
    
    return {
        'available': available,
        'missing': missing,
        'all_available': len(missing) == 0
    }

def find_wechat_window_advanced():
    """使用多种方法查找微信窗口"""
    try:
        import win32gui
        import win32con
        
        windows = []
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    window_text = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # 多种匹配条件
                    if any(keyword in window_text.lower() for keyword in ['微信', 'wechat']):
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'class': class_name,
                            'rect': rect,
                            'x': rect[0], 'y': rect[1],
                            'width': rect[2] - rect[0],
                            'height': rect[3] - rect[1]
                        })
                except:
                    pass
            return True
        
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        # 按窗口大小排序，通常微信主窗口比较大
        windows.sort(key=lambda w: w['width'] * w['height'], reverse=True)
        
        return windows
    except ImportError:
        return []

def activate_wechat_window():
    """激活微信窗口的多种方法"""
    try:
        import win32gui
        import win32con
        import pyautogui
        
        # 方法1: 查找微信窗口
        windows = find_wechat_window_advanced()
        if windows:
            wechat_window = windows[0]
            win32gui.ShowWindow(wechat_window['hwnd'], win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(wechat_window['hwnd'])
            time.sleep(1)
            return True
        
        # 方法2: 使用Alt+Tab切换到微信
        pyautogui.hotkey('alt', 'tab')
        time.sleep(1)
        
        # 方法3: 尝试点击任务栏的微信图标
        # 这里需要根据实际情况调整坐标
        screen_width, screen_height = pyautogui.size()
        taskbar_y = screen_height - 40  # 任务栏通常在底部
        
        # 尝试点击任务栏左侧的微信图标
        pyautogui.click(100, taskbar_y)
        time.sleep(1)
        
        return True
        
    except ImportError:
        return False

@mcp.tool()
def check_environment() -> dict:
    """检查运行环境"""
    deps = check_dependencies()
    wechat_path = find_wechat_path()
    windows = find_wechat_window_advanced()
    
    return {
        "success": True,
        "dependencies": deps,
        "wechat_path": wechat_path,
        "wechat_installed": wechat_path is not None,
        "wechat_windows": len(windows),
        "message": "环境检查完成"
    }

@mcp.tool()
def open_wechat() -> dict:
    """打开微信应用"""
    try:
        # 检查微信是否已经运行
        result = safe_subprocess_run(['tasklist', '/FI', f'IMAGENAME eq {WECHAT_PROCESS_NAME}'])
        
        if WECHAT_PROCESS_NAME in result.stdout:
            return {"success": True, "message": "微信已经在运行中"}
        
        # 尝试直接启动微信
        wechat_path = find_wechat_path()
        if wechat_path:
            subprocess.Popen([wechat_path])
            time.sleep(5)  # 增加等待时间
            return {"success": True, "message": f"微信启动成功 (路径: {wechat_path})"}
        else:
            # 如果找不到路径，尝试使用start命令
            subprocess.Popen(['start', WECHAT_APP_NAME], shell=True)
            time.sleep(5)
            return {"success": True, "message": "微信启动成功 (使用start命令)"}
            
    except Exception as e:
        logger.error(f"启动微信失败: {e}")
        return {"success": False, "message": f"启动微信失败: {str(e)}"}

@mcp.tool()
def close_wechat() -> dict:
    """关闭微信应用"""
    try:
        result = safe_subprocess_run(['taskkill', '/F', '/IM', WECHAT_PROCESS_NAME])
        return {"success": True, "message": "微信已关闭"}
    except Exception as e:
        logger.error(f"关闭微信失败: {e}")
        return {"success": False, "message": f"关闭微信失败: {str(e)}"}

@mcp.tool()
def get_wechat_status() -> dict:
    """获取微信运行状态"""
    try:
        result = safe_subprocess_run(['tasklist', '/FI', f'IMAGENAME eq {WECHAT_PROCESS_NAME}'])
        is_running = WECHAT_PROCESS_NAME in result.stdout
        windows = find_wechat_window_advanced()
        
        return {
            "success": True,
            "is_running": is_running,
            "window_count": len(windows),
            "message": "微信正在运行" if is_running else "微信未运行",
            "wechat_path": find_wechat_path()
        }
    except Exception as e:
        logger.error(f"获取微信状态失败: {e}")
        return {"success": False, "message": f"获取微信状态失败: {str(e)}"}

@mcp.tool()
def list_wechat_windows() -> dict:
    """列出所有微信相关窗口"""
    try:
        windows = find_wechat_window_advanced()
        
        return {
            "success": True,
            "windows": windows,
            "count": len(windows),
            "message": f"找到 {len(windows)} 个微信相关窗口"
        }
    except Exception as e:
        logger.error(f"列出微信窗口失败: {e}")
        return {"success": False, "message": f"列出微信窗口失败: {str(e)}"}

@mcp.tool()
def open_wechat_chat(contact_name: str) -> dict:
    """打开微信某个联系人的对话框"""
    try:
        # 检查依赖
        deps = check_dependencies()
        if not deps['all_available']:
            return {
                "success": False,
                "message": f"缺少依赖库: {', '.join(deps['missing'])}。请运行: pip install {' '.join(deps['missing'])}"
            }
        
        # 确保微信已启动
        open_result = open_wechat()
        if not open_result["success"]:
            return open_result
    
        
        # 激活微信窗口
        if not activate_wechat_window():
            return {"success": False, "message": "无法激活微信窗口"}
        
        import pyautogui
        import pyperclip
        
        # 使用Ctrl+F打开搜索
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # 输入联系人姓名
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        # 按回车键打开对话框
        pyautogui.press('enter')
        time.sleep(0.5)
        
        return {
            "success": True,
            "message": f"已尝试打开联系人 {contact_name} 的对话框"
        }
        
    except Exception as e:
        logger.error(f"打开联系人对话框失败: {e}")
        return {"success": False, "message": f"打开联系人对话框失败: {str(e)}"}

@mcp.tool()
def send_wechat_message(contact_name: str, message: str) -> dict:
    """打开某个对话框并且发送消息"""
    try:
        # 检查依赖
        deps = check_dependencies()
        if not deps['all_available']:
            return {
                "success": False,
                "message": f"缺少依赖库: {', '.join(deps['missing'])}。请运行: pip install {' '.join(deps['missing'])}"
            }
        
        # 首先打开联系人对话框
        chat_result = open_wechat_chat(contact_name)
        if not chat_result["success"]:
            return chat_result
        
        time.sleep(1)
        
        import pyautogui
        import pyperclip
        
        # 输入消息内容
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        # 按回车键发送消息
        pyautogui.press('enter')
        
        return {
            "success": True,
            "message": f"已尝试向 {contact_name} 发送消息",
            "sent_message": message
        }
        
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return {"success": False, "message": f"发送消息失败: {str(e)}"}

@mcp.tool()
def open_wechat_moments() -> dict:
    """打开微信朋友圈"""
    try:
        # 检查依赖
        deps = check_dependencies()
        if not deps['all_available']:
            return {
                "success": False,
                "message": f"缺少依赖库: {', '.join(deps['missing'])}。请运行: pip install {' '.join(deps['missing'])}"
            }
        
        # 确保微信已启动
        open_result = open_wechat()
        if not open_result["success"]:
            return open_result
        
        time.sleep(3)
        
        # 激活微信窗口
        if not activate_wechat_window():
            return {"success": False, "message": "无法激活微信窗口"}
        
        import pyautogui
        
        # 尝试点击朋友圈按钮位置
        # 使用相对坐标，基于屏幕中心
        screen_width, screen_height = pyautogui.size()
        
        # 朋友圈通常在左侧导航栏
        moments_x = screen_width * 0.1  # 屏幕宽度的10%位置
        moments_y = screen_height * 0.3  # 屏幕高度的30%位置
        
        pyautogui.click(moments_x, moments_y)
        time.sleep(1)
        
        return {
            "success": True,
            "message": "已尝试打开微信朋友圈",
            "click_position": {"x": moments_x, "y": moments_y}
        }
        
    except Exception as e:
        logger.error(f"打开朋友圈失败: {e}")
        return {"success": False, "message": f"打开朋友圈失败: {str(e)}"}

@mcp.tool()
def open_wechat_channels() -> dict:
    """打开微信视频号"""
    try:
        # 检查依赖
        deps = check_dependencies()
        if not deps['all_available']:
            return {
                "success": False,
                "message": f"缺少依赖库: {', '.join(deps['missing'])}。请运行: pip install {' '.join(deps['missing'])}"
            }
        
        # 确保微信已启动
        open_result = open_wechat()
        if not open_result["success"]:
            return open_result
        
        time.sleep(3)
        
        # 激活微信窗口
        if not activate_wechat_window():
            return {"success": False, "message": "无法激活微信窗口"}
        
        import pyautogui
        
        # 尝试点击视频号按钮位置
        screen_width, screen_height = pyautogui.size()
        
        # 视频号通常在左侧导航栏
        channels_x = screen_width * 0.1  # 屏幕宽度的10%位置
        channels_y = screen_height * 0.4  # 屏幕高度的40%位置
        
        pyautogui.click(channels_x, channels_y)
        time.sleep(1)
        
        return {
            "success": True,
            "message": "已尝试打开微信视频号",
            "click_position": {"x": channels_x, "y": channels_y}
        }
        
    except Exception as e:
        logger.error(f"打开视频号失败: {e}")
        return {"success": False, "message": f"打开视频号失败: {str(e)}"}

@mcp.tool()
def get_screen_info() -> dict:
    """获取屏幕信息"""
    try:
        deps = check_dependencies()
        if not deps['available'].get('pyautogui', False):
            return {
                "success": False,
                "message": "需要安装pyautogui: pip install pyautogui"
            }
        
        import pyautogui
        
        screen_width, screen_height = pyautogui.size()
        mouse_x, mouse_y = pyautogui.position()
        
        return {
            "success": True,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "mouse_position": {"x": mouse_x, "y": mouse_y},
            "message": "屏幕信息获取成功"
        }
    except Exception as e:
        logger.error(f"获取屏幕信息失败: {e}")
        return {"success": False, "message": f"获取屏幕信息失败: {str(e)}"}

if __name__ == "__main__":
    print("WeChat Control Simple MCP backend started.")
    print("=" * 50)
    
    # 检查环境
    deps = check_dependencies()
    if not deps['all_available']:
        print("⚠️  缺少依赖库:")
        for missing in deps['missing']:
            print(f"   - {missing}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(deps['missing'])}")
    else:
        print("✅ 所有依赖库已安装")
    
    wechat_path = find_wechat_path()
    if wechat_path:
        print(f"✅ 微信已安装: {wechat_path}")
    else:
        print("⚠️  未找到微信安装路径")
    
    windows = find_wechat_window_advanced()
    print(f"🔍 找到 {len(windows)} 个微信相关窗口")
    
    print("=" * 50)
    mcp.run(transport="stdio") 
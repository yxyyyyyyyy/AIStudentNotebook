import logging
import sys
import io
import time
import re
from mcp.server.fastmcp import FastMCP
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# 编码设置
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    encoding="utf-8",
)
logger = logging.getLogger("AudioControlMCP")

mcp = FastMCP("Audio Control")

class AudioController:
    def __init__(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = interface.QueryInterface(IAudioEndpointVolume)
            logger.info("音频控制初始化成功")
        except Exception as e:
            logger.error(f"音频控制初始化失败: {e}")
            raise

    def get_volume(self) -> int:
        """获取当前系统电脑音量，返回0-100整数百分比"""
        level = self.volume.GetMasterVolumeLevelScalar()
        return int(level * 100)

    def set_volume(self, level: int) -> bool:
        """设置系统电脑音量，level范围0-100"""
        try:
            level = max(0, min(100, level))
            scalar = level / 100
            logger.info(f"设置电脑音量: {level}%")
            self.volume.SetMasterVolumeLevelScalar(scalar, None)
            time.sleep(0.1)
            # 读取确认
            new_level = int(self.volume.GetMasterVolumeLevelScalar() * 100)
            logger.info(f"设置后电脑音量实际值: {new_level}%")
            return abs(new_level - level) <= 2  # 允许2%误差
        except Exception as e:
            logger.error(f"设置电脑音量失败: {e}")
            return False

    # 新增静音相关方法：
    def mute(self) -> bool:
        """静音电脑"""
        try:
            self.volume.SetMute(1, None)
            time.sleep(0.1)
            muted = self.volume.GetMute()
            logger.info(f"执行静音，当前静音状态: {muted}")
            return muted == 1
        except Exception as e:
            logger.error(f"静音失败: {e}")
            return False

    def unmute(self) -> bool:
        """取消静音"""
        try:
            self.volume.SetMute(0, None)
            time.sleep(0.1)
            muted = self.volume.GetMute()
            logger.info(f"取消静音，当前静音状态: {muted}")
            return muted == 0
        except Exception as e:
            logger.error(f"取消静音失败: {e}")
            return False

    def is_muted(self) -> bool:
        """获取当前静音状态，返回True或False"""
        try:
            muted = self.volume.GetMute()
            return bool(muted)
        except Exception as e:
            logger.error(f"获取静音状态失败: {e}")
            return False


audio_ctrl = None

def get_audio_ctrl() -> AudioController:
    global audio_ctrl
    if audio_ctrl is None:
        audio_ctrl = AudioController()
    return audio_ctrl

@mcp.tool()
def get_volume() -> dict:
    ctrl = get_audio_ctrl()
    try:
        vol = ctrl.get_volume()
        return {"success": True, "volume": vol, "message": f"当前电脑音量是 {vol}%"}
    except Exception as e:
        logger.error(f"获取电脑音量失败: {e}")
        return {"success": False, "message": "获取电脑音量失败"}

@mcp.tool()
def set_volume(level: int) -> dict:
    ctrl = get_audio_ctrl()
    try:
        if ctrl.set_volume(level):
            return {"success": True, "message": f"电脑音量已设置为 {level}%"}
        else:
            return {"success": False, "message": "电脑音量设置失败"}
    except Exception as e:
        logger.error(f"设置电脑音量失败: {e}")
        return {"success": False, "message": "设置电脑音量时发生异常"}

# 新增静音控制的 MCP 接口
@mcp.tool()
def mute() -> dict:
    ctrl = get_audio_ctrl()
    try:
        if ctrl.mute():
            return {"success": True, "message": "电脑已静音"}
        else:
            return {"success": False, "message": "静音失败"}
    except Exception as e:
        logger.error(f"静音失败: {e}")
        return {"success": False, "message": "执行静音时发生异常"}

@mcp.tool()
def unmute() -> dict:
    ctrl = get_audio_ctrl()
    try:
        if ctrl.unmute():
            return {"success": True, "message": "电脑已取消静音"}
        else:
            return {"success": False, "message": "取消静音失败"}
    except Exception as e:
        logger.error(f"取消静音失败: {e}")
        return {"success": False, "message": "执行取消静音时发生异常"}

@mcp.tool()
def get_mute_status() -> dict:
    ctrl = get_audio_ctrl()
    try:
        muted = ctrl.is_muted()
        return {"success": True, "muted": muted, "message": f"当前静音状态: {'已静音' if muted else '未静音'}"}
    except Exception as e:
        logger.error(f"获取静音状态失败: {e}")
        return {"success": False, "message": "获取静音状态失败"}

@mcp.tool()
def handle_command(text: str) -> dict:
    """
    简单唤醒词识别和电脑音量控制解析。
    支持：
    - 查询电脑音量：用户说“现在电脑音量多少”“告诉我当前电脑音量”等
    - 设置电脑音量：用户说“调到50%电脑音量”“把电脑音量调到70”“电脑音量设置30”等
    - 静音操作：用户说“静音”“帮我静音”“把电脑静音”“关闭声音”等
    - 取消静音：用户说“取消静音”“解除静音”“打开声音”“关闭静音”等
    """
    ctrl = get_audio_ctrl()

    # 查询音量意图
    if any(kw in text for kw in ["多少电脑音量", "现在电脑音量", "当前电脑音量", "电脑音量多少", "电脑音量几分贝"]):
        vol = ctrl.get_volume()
        return {"success": True, "message": f"当前电脑音量是 {vol}%"}

    # 设置音量意图
    m = re.search(r"电脑音量.*?(\d{1,3})", text)
    if m:
        level = int(m.group(1))
        level = max(0, min(100, level))
        success = ctrl.set_volume(level)
        if success:
            return {"success": True, "message": f"已将电脑音量设置为 {level}%"}
        else:
            return {"success": False, "message": "设置电脑音量失败"}

    # 静音意图
    if any(kw in text for kw in ["静音", "帮我静音", "把电脑静音", "关闭声音"]):
        success = ctrl.mute()
        if success:
            return {"success": True, "message": "电脑已静音"}
        else:
            return {"success": False, "message": "静音失败"}

    # 取消静音意图
    if any(kw in text for kw in ["取消静音", "解除静音", "打开声音", "关闭静音"]):
        success = ctrl.unmute()
        if success:
            return {"success": True, "message": "电脑已取消静音"}
        else:
            return {"success": False, "message": "取消静音失败"}

    return {"success": False, "message": "未识别到有效的电脑音量控制指令"}

if __name__ == "__main__":
    try:
        audio_ctrl = AudioController()
    except Exception:
        logger.error("音频控制初始化失败，程序退出")
        sys.exit(1)
    logger.info("Audio Control MCP 启动成功")
    mcp.run(transport="stdio")

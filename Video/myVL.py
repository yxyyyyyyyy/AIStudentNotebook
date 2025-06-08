# -*- coding: utf-8 -*-
import os
import cv2
import base64
import logging
import platform
import time
import threading
from typing import Optional
from mcp.server.fastmcp import FastMCP
from openai import OpenAI, APIConnectionError, APIError
import sys
import io

# 实现外置摄像头，不是小智本身的，是电脑上的摄像头进行物体识别，但是跟电脑性能有关系，可能会超时
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置结构化日�?
logger = logging.getLogger("VisionTool")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 带自动关闭的摄像头管理器
class CameraManager:
    _instance = None
    _lock = threading.Lock()
    _last_used = 0
    IDLE_TIMEOUT = 3  # 3秒无操作自动关闭
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cap = None
                cls._instance._init_time = 0
        return cls._instance
    
    def get_camera(self):
        """获取摄像头实例，如果闲置超时则重新初始化"""
        current_time = time.time()
        
        # 检查是否需要重新初始化
        if self._cap is None or not self._cap.isOpened():
            self._init_camera()
        elif current_time - self._last_used > self.IDLE_TIMEOUT:
            logger.info("摄像头闲置超时，重新初始�?")
            self.release()
            self._init_camera()
        
        self._last_used = current_time
        return self._cap
    
    def _init_camera(self):
        """初始化摄像头"""
        if platform.system() == 'Darwin':
            os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
        
        self._cap = cv2.VideoCapture(0)
        if not self._cap.isOpened():
            logger.error("摄像头访问被拒绝，请检查系统权�?")
            raise PermissionError("Camera access denied")
        
        # 优化摄像头参�?
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._cap.set(cv2.CAP_PROP_FPS, 30)
        # 设置缓冲区大小为1，确保获取最新帧
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        logger.info("摄像头初始化完成")
    
    def get_frame(self) -> Optional[bytes]:
        """获取当前帧，确保刷新缓冲区获取最新图�?"""
        cap = self.get_camera()
        
        # 刷新缓冲区，丢弃旧帧
        for _ in range(2):
            cap.grab()
        
        ret, frame = cap.read()
        if not ret:
            return None
        
        # 单次压缩
        _, buffer = cv2.imencode('.jpg', frame, [
            cv2.IMWRITE_JPEG_QUALITY, 75,
            cv2.IMWRITE_JPEG_OPTIMIZE, 1
        ])
        return buffer
    
    def release(self):
        """释放摄像头资�?"""
        if self._cap and self._cap.isOpened():
            self._cap.release()
            self._cap = None
            logger.info("摄像头资源已释放")
    
    def __del__(self):
        self.release()

# 带时间验证的API客户�?
class VisionAnalyzer:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_client()
        return cls._instance
    
    def _init_client(self):
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("未设置DASHSCOPE_API_KEY环境变量")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.cache = {}
        self.cache_lock = threading.Lock()
        logger.info("API客户端初始化完成")

    def analyze_image(self, image_data: str, timestamp: float) -> dict:
        """带时间验证的图像分析"""
        # 使用图像哈希+时间戳作为缓存键
        cache_key = f"{hash(image_data)}-{timestamp}"
        
        with self.cache_lock:
            if cache_key in self.cache:
                logger.debug("使用缓存结果")
                return self.cache[cache_key]
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model="qwen-vl-plus",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "用不耐烦的语气简单描述图片内�?"},
                        {"type": "image_url", 
                         "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }],
                timeout=8
            )
            
            result_text = response.choices[0].message.content[:500]
            
            # 添加不耐烦语气
            if "这不就是" not in result_text:
                result_text = "害，这不就是" + result_text.lstrip("这是")
            
            result = {
                "success": True,
                "result": result_text
            }
            
            with self.cache_lock:
                self.cache[cache_key] = result
                if len(self.cache) > 20:  # 限制缓存大小
                    self.cache.pop(next(iter(self.cache)))
            
            logger.info(f"API调用耗时: {time.time()-start_time:.2f}s")
            return result
        except (APIConnectionError, APIError) as e:
            logger.error(f"API错误: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"分析异常: {str(e)}")
            return {"success": False, "error": "分析失败"}

# 视觉系统
class VisionSystem:
    def __init__(self):
        self.camera = CameraManager()
        self.analyzer = VisionAnalyzer()
    
    def capture_image(self) -> Optional[str]:
        """获取当前图像"""
        try:
            start_time = time.time()
            buffer = self.camera.get_frame()
            if buffer is None:
                return None
            
            image_data = base64.b64encode(buffer).decode('utf-8')
            logger.info(f"图像捕获耗时: {time.time()-start_time:.2f}s")
            return image_data
        except Exception as e:
            logger.error(f"捕获异常: {str(e)}")
            return None

# 创建MCP服务实例
mcp = FastMCP("VisionAssistant")

@mcp.tool()
def vision_assistant(command: str) -> dict:
    """
    视觉感知系统
    命令示例：看看这是什�?/描述当前场景/睁开眼看�?
    
    返回格式�?
    {
        "success": bool,     # 是否执行成功
        "result": str,       # 分析结果文本
        "error": str         # 错误信息（可选）
    }
    """
    # 快速命令检�?
    keywords = ("�?", "查看", "睁开", "描述", "什�?", "东西")
    if not any(kw in command for kw in keywords):
        return {"success": False, "error": "无效命令"}
    
    try:
        vs = VisionSystem()
        start_time = time.time()
        
        if image_data := vs.capture_image():
            # 使用当前时间戳确保每次调用都是唯一�?
            timestamp = time.time()
            result = vs.analyzer.analyze_image(image_data, timestamp)
            logger.info(result)
            total_time = time.time() - start_time
            logger.info(f"总处理时�?: {total_time:.2f}s")
            return result
        
        return {"success": False, "error": "图像捕获失败"}
    except Exception as e:
        logger.error(f"系统错误: {str(e)}", exc_info=True)
        return {"success": False, "error": "内部错误"}

if __name__ == "__main__":
    try:
        # 注册退出清�?
        import atexit
        atexit.register(lambda: CameraManager().release())
        
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("服务已停�?")
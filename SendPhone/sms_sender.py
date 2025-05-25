from mcp.server.fastmcp import FastMCP
import requests
import logging
import sys
import io
import threading

# UTF-8 兼容处理
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("sms_sender")

# 初始化 MCP
mcp = FastMCP("SmsSender")

# 互亿无线短信 API 配置
API_ID = 'C74785358'
API_KEY = '0cf58fd6c94c17690113387e21f908d1'
SMS_API_URL = "http://106.ihuyi.com/webservice/sms.php?method=Submit"

def _send_sms_async(phone: str, content: str):
    try:
        payload = {
            "account": API_ID,
            "password": API_KEY,
            "mobile": phone,
            "content": content
        }
        response = requests.post(SMS_API_URL, data=payload, timeout=10)
        logger.info(f"短信发送响应: {response.text}")
    except Exception as e:
        logger.error(f"发送短信失败: {e}", exc_info=True)

@mcp.tool()
def send_sms(phone: str, code: str) -> dict:
    """
    发送短信验证码
    参数：
      phone: 手机号
      code: 验证码
    """
    try:
        content = f"您的验证码是：{code}。请不要把验证码泄露给其他人。"
        threading.Thread(target=_send_sms_async, args=(phone, content), daemon=True).start()
        logger.info(f"开始异步发送短信至 {phone}")
        return {"success": True, "message": f"开始异步发送短信到 {phone}"}
    except Exception as e:
        error_msg = f"短信发送异常：{e}"
        logger.error(error_msg, exc_info=True)
        return {"success": False, "error": error_msg}

# 启动 MCP 服务
if __name__ == "__main__":
    mcp.run(transport="stdio")

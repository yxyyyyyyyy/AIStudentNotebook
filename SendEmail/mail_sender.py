# 发送qq邮箱 需要授权码 但是会有qq发送和mcp联通的线程问题
from mcp.server.fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging
import sys
import io
import threading

# 确保 stdin/stdout 使用 UTF-8
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("mail_sender")

# 初始化 MCP
mcp = FastMCP("MailSender")

# 邮箱配置
EMAIL_ACCOUNT = "3436771164@qq.com"
EMAIL_AUTH_CODE = "vzldyriycecddaej"  # 授权码，不是密码
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

# SMTP 真正发送过程中出现了“阻塞”或“破坏了标准输出流”，导致 MCP 或语音系统无法接收到预期的返回结果或输出
def _send_email_async(to_email: str, msg: MIMEText):
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.login(EMAIL_ACCOUNT, EMAIL_AUTH_CODE)
            server.sendmail(EMAIL_ACCOUNT, [to_email], msg.as_string())
        logger.info(f"异步邮件发送成功: {to_email}")
    except Exception as e:
        logger.error(f"异步邮件发送失败: {e}", exc_info=True)
@mcp.tool()
def send_mail(to: str, subject: str, content: str) -> dict:
    """
    向指定邮箱发送邮件。如果只传入数字字符串，则自动识别为QQ号，拼成QQ邮箱地址。
    """
    try:
        to_email = f"{to}@qq.com" if to.isdigit() else to

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = EMAIL_ACCOUNT
        msg["To"] = to_email

        # 异步发送邮件，避免阻塞和破坏标准输出
        threading.Thread(target=_send_email_async, args=(to_email, msg), daemon=True).start()

        logger.info(f"开始异步发送邮件至 {to_email}")
        return {"success": True, "message": f"开始异步发送邮件到 {to_email}"}

    except Exception as e:
        error_msg = f"邮件发送异常：{e}"
        logger.error(error_msg, exc_info=True)
        return {"success": False, "error": error_msg}


# 启动 MCP 服务
if __name__ == "__main__":
    mcp.run(transport="stdio")

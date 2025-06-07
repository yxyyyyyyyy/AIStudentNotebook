from mcp.server.fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("mail_sender")

mcp = FastMCP("MailSender")

EMAIL_ACCOUNT = "3436771164@qq.com"
EMAIL_AUTH_CODE = "vzldyriycecddaej"  # 授权码，不是密码
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465

@mcp.tool()
def send_mail(to: str, subject: str, content: str) -> dict:
    """
    向指定邮箱发送邮件。如果只传入数字字符串，则自动识别为QQ号，拼成QQ邮箱地址。
    """
    try:
        # 自动检测是否只包含数字，若是，自动拼成 QQ 邮箱
        if to.isdigit():
            to_email = f"{to}@qq.com"
        else:
            to_email = to

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = EMAIL_ACCOUNT
        msg["To"] = to_email

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ACCOUNT, EMAIL_AUTH_CODE)
            server.sendmail(EMAIL_ACCOUNT, [to_email], msg.as_string())

        logger.info(f"邮件已发送至 {to_email}")
        return {"success": True, "message": f"已成功发送邮件到 {to_email}"}

    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")

import os
import re
import logging
import sys
import io
from mcp.server.fastmcp import FastMCP

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
logger = logging.getLogger("FileManagerMCP")

mcp = FastMCP("FileManager")

# 你想管理的根目录，所有操作都限定在这里，避免误操作系统其它目录
ROOT_DIR = os.path.abspath("./file_root")
os.makedirs(ROOT_DIR, exist_ok=True)

def safe_path(path: str) -> str:
    """保证路径在根目录内，防止目录穿越"""
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, path))
    if not abs_path.startswith(ROOT_DIR):
        raise ValueError("不允许访问根目录外路径")
    return abs_path

@mcp.tool()
def create_file(file_path: str) -> dict:
    try:
        full_path = safe_path(file_path)
        if os.path.exists(full_path):
            return {"success": False, "message": f"文件已存在: {file_path}"}
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("")  # 创建空文件
        logger.info(f"创建文件 {full_path}")
        return {"success": True, "message": f"文件创建成功: {file_path}"}
    except Exception as e:
        logger.error(f"创建文件失败: {e}")
        return {"success": False, "message": f"创建文件失败: {e}"}

@mcp.tool()
def delete_file(file_path: str) -> dict:
    try:
        full_path = safe_path(file_path)
        if not os.path.exists(full_path):
            return {"success": False, "message": f"文件不存在: {file_path}"}
        if os.path.isdir(full_path):
            # 递归删除文件夹
            import shutil
            shutil.rmtree(full_path)
            logger.info(f"删除目录 {full_path}")
            return {"success": True, "message": f"目录已删除: {file_path}"}
        else:
            os.remove(full_path)
            logger.info(f"删除文件 {full_path}")
            return {"success": True, "message": f"文件已删除: {file_path}"}
    except Exception as e:
        logger.error(f"删除失败: {e}")
        return {"success": False, "message": f"删除失败: {e}"}

@mcp.tool()
def read_file(file_path: str) -> dict:
    try:
        full_path = safe_path(file_path)
        if not os.path.isfile(full_path):
            return {"success": False, "message": f"文件不存在: {file_path}"}
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"读取文件 {full_path}")
        return {"success": True, "content": content}
    except Exception as e:
        logger.error(f"读取文件失败: {e}")
        return {"success": False, "message": f"读取文件失败: {e}"}

@mcp.tool()
def write_file(file_path: str, content: str) -> dict:
    try:
        full_path = safe_path(file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"写入文件 {full_path}")
        return {"success": True, "message": f"文件写入成功: {file_path}"}
    except Exception as e:
        logger.error(f"写入文件失败: {e}")
        return {"success": False, "message": f"写入文件失败: {e}"}

@mcp.tool()
def list_files(dir_path: str = "") -> dict:
    try:
        full_path = safe_path(dir_path)
        if not os.path.exists(full_path):
            return {"success": False, "message": f"目录不存在: {dir_path}"}
        if not os.path.isdir(full_path):
            return {"success": False, "message": f"不是目录: {dir_path}"}
        files = os.listdir(full_path)
        logger.info(f"列出目录 {full_path}")
        return {"success": True, "files": files}
    except Exception as e:
        logger.error(f"列目录失败: {e}")
        return {"success": False, "message": f"列目录失败: {e}"}

# 唤醒词列表
WAKE_WORDS = ["小助手", "助手", "嘿助手", "嗨助手"]

@mcp.tool()
def parse_command(text: str) -> dict:
    """
    简单唤醒词+意图解析示例:
    支持命令：
      - 创建文件 xxx.txt
      - 删除文件|目录 xxx
      - 读取文件 xxx
      - 写入文件 xxx 内容 ...
      - 列出目录 xxx
    """
    if not any(w in text for w in WAKE_WORDS):
        return {"success": False, "message": "未检测到唤醒词"}

    # 创建文件
    m_create = re.search(r"创建(文件|目录|文件夹)?\s*([\w\./\\]+)", text)
    if m_create:
        path = m_create.group(2)
        return create_file(file_path=path)

    # 删除文件或目录
    m_delete = re.search(r"删除(文件|目录|文件夹)?\s*([\w\./\\]+)", text)
    if m_delete:
        path = m_delete.group(2)
        return delete_file(file_path=path)

    # 读取文件
    m_read = re.search(r"(读取|打开|查看)文件\s*([\w\./\\]+)", text)
    if m_read:
        path = m_read.group(2)
        return read_file(file_path=path)

    # 写入文件，格式示例：“写入文件 test.txt 内容 这是要写入的文本”
    m_write = re.search(r"写入文件\s*([\w\./\\]+)\s*内容\s*(.+)", text)
    if m_write:
        path = m_write.group(1)
        content = m_write.group(2)
        return write_file(file_path=path, content=content)

    # 列出目录
    m_list = re.search(r"(列出|显示|查看)(目录|文件夹)?\s*([\w\./\\]*)", text)
    if m_list:
        dir_path = m_list.group(3) or ""
        return list_files(dir_path=dir_path)

    return {"success": False, "message": "未识别到有效指令"}

if __name__ == "__main__":
    logger.info("FileManager MCP 启动成功，管理根目录：" + ROOT_DIR)
    mcp.run(transport="stdio")

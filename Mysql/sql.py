import logging
import pymysql
from datetime import datetime
from mcp.server.fastmcp import FastMCP
import sys
import io

# 编码处理
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    encoding="utf-8",
)
logger = logging.getLogger("memo_mcp")

# MCP 实例
mcp = FastMCP("Memo")

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "memo_db",
    "charset": "utf8mb4"
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

# 添加备忘
def add_memo_to_db(content):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO memos (content) VALUES (%s)", (content,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"添加备忘录失败: {e}")

# 加载备忘
def load_memos():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, content, time FROM memos ORDER BY time DESC")
            result = cursor.fetchall()
        conn.close()
        return [
            {"id": row[0], "content": row[1], "time": row[2].strftime("%Y-%m-%d %H:%M:%S")}
            for row in result
        ]
    except Exception as e:
        logger.error(f"加载备忘录失败: {e}")
        return []

# 清空备忘
def clear_all_memos():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM memos")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"清空备忘录失败: {e}")

# 删除单条
def delete_memo_by_content(content):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 找出所有匹配的条目
            cursor.execute("SELECT id, content FROM memos WHERE content LIKE %s", (f"%{content}%",))
            results = cursor.fetchall()

            if not results:
                return {"success": False, "message": "未找到匹配的备忘内容。"}

            if len(results) > 1:
                matched = "\n".join([f"[{row[0]}] {row[1]}" for row in results])
                return {
                    "success": False,
                    "message": f"找到多条匹配内容，请更具体删除：\n{matched}"
                }

            # 唯一匹配，执行删除
            memo_id = results[0][0]
            cursor.execute("DELETE FROM memos WHERE id = %s", (memo_id,))
            conn.commit()
            conn.close()
            return {"success": True, "message": f"已删除备忘：{results[0][1]}"}

    except Exception as e:
        logger.error(f"删除备忘失败: {e}")
        return {"success": False, "message": "删除时发生错误。"}

# 工具函数：根据原内容模糊查找并更新
def update_memo_by_content(old_content, new_content):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # 查找匹配的记录
            cursor.execute("SELECT id, content FROM memos WHERE content LIKE %s", (f"%{old_content}%",))
            result = cursor.fetchall()

            if not result:
                return {"success": False, "message": "未找到匹配的备忘内容。"}

            if len(result) > 1:
                matched = "\n".join([f"[{row[0]}] {row[1]}" for row in result])
                return {
                    "success": False,
                    "message": f"找到多条匹配内容，请更具体：\n{matched}"
                }

            # 只找到一条，执行更新
            memo_id = result[0][0]
            cursor.execute("UPDATE memos SET content = %s WHERE id = %s", (new_content, memo_id))
            conn.commit()
            conn.close()
            return {"success": True, "message": f"已将备忘更新为：{new_content}"}

    except Exception as e:
        logger.error(f"模糊修改备忘失败: {e}")
        return {"success": False, "message": "修改时发生错误。"}


@mcp.tool()
def update_memo(old_content: str, new_content: str) -> dict:
    logger.info(f"update_memo called with old_content='{old_content}', new_content='{new_content}'")
    return update_memo_by_content(old_content, new_content)


# MCP 工具函数
@mcp.tool()
def add_memo(content: str) -> dict:
    logger.info(f"add_memo called with content: {content}")
    add_memo_to_db(content)
    return {"success": True, "message": f"已添加备忘：{content}"}

@mcp.tool()
def list_memos() -> dict:
    logger.info("list_memos called")
    memos = load_memos()
    if not memos:
        return {"success": True, "memos": "当前没有备忘内容。"}
    return {
        "success": True,
        "memos": "\n".join([f"[{m['id']}] {m['time']} - {m['content']}" for m in memos])
    }

@mcp.tool()
def clear_memos() -> dict:
    logger.info("clear_memos called")
    clear_all_memos()
    return {"success": True, "message": "所有备忘已清空。"}


@mcp.tool()
def delete_memo(content: str) -> dict:
    logger.info(f"delete_memo called with content: {content}")
    return delete_memo_by_content(content)


# 启动
if __name__ == "__main__":
    print("MCP Memo backend starting...", flush=True)
    mcp.run(transport="stdio")

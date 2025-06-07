import logging
import sys

import requests
from mcp.server.fastmcp import FastMCP
import json


# 日志设置
logger = logging.getLogger("coze_workflow")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.__stdout__)  # 使用原始标准输出
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# MCP 初始化
mcp = FastMCP("CozeWorkflow")

@mcp.tool()
def coze_workflow_echo(content: str) -> dict:
    """
    使用 Coze Workflow 提问，支持生成台词、查询信息等。

    参数:
    - content: 用户输入的提问内容，例如:
        - 请给我一句鼓励自己的台词
        - 查询一下历史上的今天发生了什么
        - 给我一段哲理句子

    返回:
    - 包含以下字段的字典:
        - success: 是否成功
        - question: 用户原始问题
        - answer: Coze Workflow 返回的文本内容
    """
    logger.info(f"🔥 run_coze_workflow 被调用，参数: {content}")
    try:
        if not content.strip():
            return {"success": False, "message": "请输入有效的问题。"}

        # 设置访问参数
        ACCESS_TOKEN = "pat_NmS1sj4WlA8Znn5DKivPYnkC8qzQlSuaJ6yDElMoF97O7tcrE8zCdCKSWQChijuC"
        WORKFLOW_ID = "7513027836551512079"
        PARAMETERS = {
            "content": content
        }

        url = "https://api.coze.cn/v1/workflow/stream_run"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "workflow_id": WORKFLOW_ID,
            "parameters": PARAMETERS
        }

        logger.info(f"请求 URL: {url}")
        logger.info(f"请求 Headers: {headers}")
        logger.info(f"请求 Payload: {json.dumps(payload, ensure_ascii=False)}")

        final_result = []

        with requests.post(url, json=payload, headers=headers, stream=True) as resp:
            resp.raise_for_status()
            final_result = []
            for line_bytes in resp.iter_lines(decode_unicode=False):  # 先拿 bytes
                if not line_bytes:
                    continue
                try:
                    # 尝试 UTF-8 解码
                    try:
                        line = line_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        # UTF-8 解码失败，尝试 gb18030
                        line = line_bytes.decode('gb18030')

                    logger.info(f"接收到行（解码后）: {line}")
                    line = line.strip()
                    if line.startswith("data:"):
                        data_str = line[len("data:"):].strip()
                        if not data_str or data_str == "[DONE]":
                            continue
                        event = json.loads(data_str)
                        content = event.get("content", "")
                        if content:
                            # content一般是正常字符串，不用额外解码
                            final_result.append(content)
                except Exception as e:
                    logger.warning(f"处理数据时异常: {e}")



        answer = "".join(final_result)
        logger.info(f"最终拼接内容: {final_result}")
        return {
            "success": True,
            "question": content,
            "answer": answer or "未获取到回复内容"
        }

    except Exception as e:
        logger.error(f"Coze 工作流执行失败: {e}")
        return {"success": False, "message": "请求失败"}
    
if __name__ == "__main__":
    logger.info("🟢 MCP 开始运行...")
    mcp.run(transport="stdio")

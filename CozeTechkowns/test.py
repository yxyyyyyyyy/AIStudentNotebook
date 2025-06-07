import requests

def run_coze_workflow_stream(token, workflow_id, parameters=None, bot_id=None, app_id=None):
    url = "https://api.coze.cn/v1/workflow/stream_run"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "workflow_id": workflow_id
    }
    if parameters:
        payload["parameters"] = parameters
    if bot_id:
        payload["bot_id"] = bot_id
    if app_id:
        payload["app_id"] = app_id

    # 开启流式请求
    with requests.post(url, json=payload, headers=headers, stream=True) as resp:
        resp.raise_for_status()
        
        # 读取流数据，逐行处理
        for line in resp.iter_lines():
            if line:
                # 扣子流式响应是 SSE 格式，例如：
                # id: 0
                # event: Message
                # data: {"content":"msg","node_is_finish":false,...}
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[len("data: "):]
                    print("Event data:", data_str)
                else:
                    print("Other line:", decoded_line)

if __name__ == "__main__":
    # 请替换成你的真实 Access Token 和 Workflow ID
    ACCESS_TOKEN = "pat_NmS1sj4WlA8Znn5DKivPYnkC8qzQlSuaJ6yDElMoF97O7tcrE8zCdCKSWQChijuC"
    WORKFLOW_ID = "7513027836551512079"
    PARAMETERS = {
        "content": "全球高考"
    }


    run_coze_workflow_stream(ACCESS_TOKEN, WORKFLOW_ID, PARAMETERS)

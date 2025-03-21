import csv
from typing import Type, Optional
import requests
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.messages import HumanMessage
from langchain.tools.base import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor
from pydantic import BaseModel, Field


def find_code(csv_file_path, district_name) -> str:
    """
    根据区域或者城市的名字，返回该区域的编码
    :param csv_file_path:
    :param district_name:
    :return:
    """
    district_map = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            district_code = row['districtcode'].strip()
            district = row['district'].strip()
            if district not in district_map:
                district_map[district] = district_code

    return district_map.get(district_name, None)


class WeatherInputArgs(BaseModel):
    """Input的Schema类"""
    location: str = Field(..., description='用于查询天气的位置信息')


class WeatherTool(BaseTool):
    """查询实时天气的工具"""
    name: str = 'weather_tool'  # 添加类型注解
    description: str = '可以查询任意位置的当前天气情况'
    args_schema: Type[WeatherInputArgs] = WeatherInputArgs

    def _run(
            self,
            location: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """就是调用工具的时候，自动执行的函数"""
        district_code = find_code('weather_district_id.csv', location)
        print(f'需要查询的{location}, 的地区编码是: {district_code}')
        if not district_code:
            return f"未找到 {location} 的地区编码，请检查输入是否正确。"

        url = f'https://api.map.baidu.com/weather/v1/?district_id={district_code}&data_type=now&ak=3Z1CiOUZs3EhU3WY6GBermZgH8IUd2wk'

        # 发送请求
        response = requests.get(url)
        if response.status_code != 200:
            return f"请求天气数据失败，状态码: {response.status_code}"

        data = response.json()
        if data.get('status') != 0:
            return f"查询天气失败，错误信息: {data.get('message')}"

        result = data.get('result', {}).get('now', {})
        text = result.get('text', '未知')
        temp = result.get('temp', '未知')
        feels_like = result.get('feels_like', '未知')
        rh = result.get('rh', '未知')
        wind_dir = result.get('wind_dir', '未知')
        wind_class = result.get('wind_class', '未知')

        return f"位置: {location} 当前天气: {text}，温度: {temp} °C，体感温度: {feels_like} °C，相对湿度：{rh} %，{wind_dir}:{wind_class}"


if __name__ == '__main__':
    # 创建模型
    model = ChatOpenAI(
        model='glm-4-0520',
        temperature=0.6,
        api_key='bfa7f4a5ee344bedaf2f265018374987.leHBJXH7xDUZ9z41',
        base_url='https://open.bigmodel.cn/api/paas/v4/'
    )

    tools = [WeatherTool()]

    agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)

    resp = agent_executor.invoke({'messages': [HumanMessage(content='中国的首都是哪个城市？')]})
    print(resp['messages'])

    resp2 = agent_executor.invoke({'messages': [HumanMessage(content='广州天气怎么样？')]})
    print(resp2['messages'])

    if len(resp2['messages']) > 2:
        print(resp2['messages'][2].content)
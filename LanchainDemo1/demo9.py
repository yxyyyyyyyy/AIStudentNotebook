import os

from langchain_experimental.synthetic_data import create_data_generation_chain
from langchain_openai import ChatOpenAI
# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"

# 聊天机器人案例
# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 创建链
chain = create_data_generation_chain(model)

# 生成一些文本数据
result = chain(
    {
        "fields": {"颜色": ['蓝色', '黄色'] , "人物":['蒋丞','顾飞']},
        "preferences": {"style": "短篇小说,要美好,向上,有点色情在"}
    }
)
print(result.get("text"))
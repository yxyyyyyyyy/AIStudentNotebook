import os

from langchain_experimental.synthetic_data import create_data_generation_chain
from langchain_openai import ChatOpenAI

os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"
os.environ["LANGCHAIN_API_KEY"] = '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'
# os.environ["TAVILY_API_KEY"] = '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'

# 聊天机器人案例
# 创建模型
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.8)

# 创建链
chain = create_data_generation_chain(model)

# 生成数据
# result = chain(  # 给于一些关键词， 随机生成一句话
#     {
#         "fields": ['蓝色', '黄色'],
#         "preferences": {}
#     }
# )

result = chain(  # 给于一些关键词， 随机生成一句话
    {
        "fields": {"颜色": ['蓝色', '黄色']},
        "preferences": {"style": "让它像诗歌一样。"}
    }
)
print(result)


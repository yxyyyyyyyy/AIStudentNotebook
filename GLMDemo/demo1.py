# GLM自己的API
from zhipuai import ZhipuAI
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.prebuilt import chat_agent_executor


client = ZhipuAI(
    api_key='bfa7f4a5ee344bedaf2f265018374987.leHBJXH7xDUZ9z41',
)

response = client.chat.completions.create(
    model='glm-4-0520',
    messages=[
        {'role': "user", 'content': '评价一下西安电子科技大学'}
    ],
    # stream=True
)

# print(response)
print(response.choices[0].message.content)

# 流试的输出
# for s in response:
#     print(s.choices[0].delta.content)
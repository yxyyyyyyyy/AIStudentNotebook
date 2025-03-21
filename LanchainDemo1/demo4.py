# 案例四：Langchian构建代理

import os
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langgraph.prebuilt import chat_agent_executor
from langchain_deepseek import ChatDeepSeek  # 使用 DeepSeek 需要安装 langchain-deepseek

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1080"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:1080"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo3"
os.environ["TAVILY_API_KEY"] = "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"

# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 没有任何代理的情况下
# print(model.invoke([HumanMessage(content="广州今天天气怎么样?")]))

# LangChain内置了一个工具，可以轻松地使用Tavily搜索引擎作为工具。 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
search = TavilySearchResults(max_results=2) #  max_results: 只返回两个结果
# print(search.invoke('广州现在的天气怎么样？'))

# 工具
tools =  [search]
#  创建代理
agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)


# resp = agent_executor.invoke({'messages': [HumanMessage(content='中国的首都是哪个城市？')]})
# print(resp['messages'])

resp2 = agent_executor.invoke({'messages': [HumanMessage(content='广州天气怎么样？')]})
print(resp2['messages'])

print(resp2['messages'][1].content)
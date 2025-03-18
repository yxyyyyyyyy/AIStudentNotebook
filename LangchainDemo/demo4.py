import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.prebuilt import chat_agent_executor
from langserve import add_routes

os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"
os.environ["LANGCHAIN_API_KEY"] = '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'
os.environ["TAVILY_API_KEY"] = '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'

# 聊天机器人案例
# 创建模型
model = ChatOpenAI(model='gpt-4-turbo')

# 没有任何代理的情况下
# result = model.invoke([HumanMessage(content='北京天气怎么样？')])
# print(result)

# LangChain内置了一个工具，可以轻松地使用Tavily搜索引擎作为工具。
search = TavilySearchResults(max_results=2)  #  max_results: 只返回两个结果
# print(search.invoke('北京的天气怎么样？'))

# 让模型绑定工具
tools = [search]
# model_with_tools = model.bind_tools(tools)
#  创建代理

agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)

resp = agent_executor.invoke({'messages': [HumanMessage(content='中国的首都是哪个城市？')]})
print(resp['messages'])

resp2 = agent_executor.invoke({'messages': [HumanMessage(content='北京天气怎么样？')]})
print(resp2['messages'])

print(resp2['messages'][2].content)

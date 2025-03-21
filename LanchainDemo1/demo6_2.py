import os
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo5"

# 🔹系统提示词（不作为 `ChatOpenAI` 的参数，而是加入消息列表）
system_prompt = """
您是一个被设计用来与SQL数据库交互的代理。
给定一个输入问题，创建一个语法正确的SQL语句并执行，然后查看查询结果并返回答案。
除非用户指定了他们想要获得的示例的具体数量，否则始终将SQL查询限制为最多10个结果。
你可以按相关列对结果进行排序，以返回MySQL数据库中最匹配的数据。
您可以使用与数据库交互的工具。在执行查询之前，你必须仔细检查。如果在执行查询时出现错误，请重写查询SQL并重试。
不要对数据库做任何DML语句(插入，更新，删除，删除等)。

首先，你应该查看数据库中的表，看看可以查询什么。
不要跳过这一步。
然后查询最相关的表的模式。
"""

# 🔹创建 OpenAI 代理（不传 `system_message`）
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 🔹初始化 MySQL 数据库
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'test1'
USERNAME = 'root'
PASSWORD = 'root'
MYSQL_URI = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4'
db = SQLDatabase.from_uri(MYSQL_URI)

# 创建工具
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# 🔹创建代理
agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)

# 🔹正确的消息调用方式
messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content="那个年龄的用户最多?")
]

# 执行查询
resp = agent_executor.invoke({'messages': messages})

# 解析并打印结果
result = resp['messages']
# print(result)
# print(len(result))
print(result[-1])  # 最后一个才是真正的答案

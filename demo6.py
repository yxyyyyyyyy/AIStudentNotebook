import os
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools import QuerySQLDataBaseTool, QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo5"

# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# sqlalchemy 初始化MySQL数据库的连接
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'test1'
USERNAME = 'root'
PASSWORD = 'root'
# mysqlclient驱动URL
MYSQL_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
db = SQLDatabase.from_uri(MYSQL_URI)
# print(db.get_usable_table_names())
# print(db.run('select * from tb_user limit 10;'))

# 直接使用大模型和数据库整合, 只能根据你的问题生成SQL
test_chain = create_sql_query_chain(model, db)
resp = test_chain.invoke({'question': '请问：员工表中有多少条数据？'})

answer_prompt = PromptTemplate.from_template(
    """给定以下用户问题、SQL语句和SQL执行后的结果，回答用户问题。
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    回答: """
)
# 创建一个执行sql语句的工具
# 1. 设置 SQL 执行工具
execute_sql_tool = QuerySQLDatabaseTool(db=db)

# 2. 生成 SQL 语句并执行
def clean_query(input_data):
    """去掉 SQL 语句中可能错误的前缀（如 'SQLQuery:'）"""
    query = input_data["query"]
    if query.startswith("SQLQuery:"):
        query = query.replace("SQLQuery:", "").strip()
    return {"query": query}

chain = (
    RunnablePassthrough.assign(query=test_chain)  # 生成 SQL 查询
    .assign(cleaned_query=clean_query)  # 清理 SQL 语句
    .assign(result=lambda x: execute_sql_tool.invoke(x["cleaned_query"]["query"]))  # 执行 SQL
    | answer_prompt  # 格式化结果
    | model  # 传递给 LLM 处理
    | StrOutputParser()  # 解析输出
)

# 3. 执行查询
rep = chain.invoke(input={"question": "请问：员工表中有多少条数据？"})

# 4. 输出结果
print(rep)
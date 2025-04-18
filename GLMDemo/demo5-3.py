import os
from operator import itemgetter

from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1080"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:1080"

# sqlalchemy 初始化MySQL数据库的连接
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'test1'
USERNAME = 'root'
PASSWORD = 'root'
# mysqlclient驱动URL
MYSQL_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

# 创建模型
model = ChatOpenAI(
    model='glm-4-0520',
    temperature=0,
    api_key='bfa7f4a5ee344bedaf2f265018374987.leHBJXH7xDUZ9z41',
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)
db = SQLDatabase.from_uri(MYSQL_URI)

create_sql = create_sql_query_chain(llm=model, db=db)

execute_sql = QuerySQLDataBaseTool(db=db)  # langchain内置的工具

create_sql = create_sql | (lambda x: x.replace("SQLQuery: ", "").split("\n")[0])
# chain = create_sql | (lambda x: x.replace('```sql', '').replace('```', '')) | execute_sql

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question. 用中文回答最终答案
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

answer_chain = answer_prompt | model | StrOutputParser()

chain = RunnablePassthrough.assign(query=create_sql).assign(result=itemgetter('query') | execute_sql) | answer_chain

resp = chain.invoke({'question': '请问：一共有多少个员工？'})
print(resp)

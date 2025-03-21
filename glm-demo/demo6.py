from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_openai import ChatOpenAI

# sqlalchemy 初始化MySQL数据库的连接
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'test_db8'
USERNAME = 'root'
PASSWORD = '123123'
# mysqlclient驱动URL
MYSQL_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

# 创建模型
model = ChatOpenAI(
    model='glm-4-0520',
    temperature=0,
    api_key='0884a4262379e6b9e98d08be606f2192.TOaCwXTLNYo1GlRM',
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)

db = SQLDatabase.from_uri(MYSQL_URI)
# print(db.dialect)
# print(db.get_usable_table_names())
# print(db.run('select * from t_emp;'))


chian = create_sql_query_chain(llm=model, db=db)
# chian.get_prompts()[0].pretty_print()
resp = chian.invoke({'question': '请问：一共有多少个员工？'})
print('大语言模型生成的SQL：' + resp)
sql = resp.replace('```sql', '').replace('```', '')
print('提取之后的SQL：' + sql)

print(db.run(sql))
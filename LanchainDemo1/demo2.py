# 案例二:Langchian构建聊天机器人
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
import os
from langchain_community.chat_message_histories import ChatMessageHistory

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1080"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:1080"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"

# 聊天机器人案例
# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 定义提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ('system', '你是一个非常乐于助人的助手.用{language}尽你所你的回答所以的问题'),
    MessagesPlaceholder(variable_name='yxy_msg')
])


# 得到链
chain = prompt_template | model

# 保存聊天的历史记录
store = {} # 所有用户的聊天记录都保存在store中 key:session

# 此函数预期将接收一个SESSION_ID并返回一个消息历史记录对象
def get_session_history(session_id:str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


do_msg = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key= 'yxy_msg' #每次聊天时候发送msg的key
)

config = {'configurable':{'session_id':'Echo123'}}

# 第一轮
resp = do_msg.invoke(
    {
        'yxy_msg':[HumanMessage(content='你好啊!我是yxy,你会记得我吗?')],
        'language':'中文'
    } ,
    config = config,
)

print(resp.content)


# 第二轮
resp2 = do_msg.invoke(
    {
        'yxy_msg':[HumanMessage(content='我的名字叫什么?')],
        'language':'中文'
    } ,
    config = config,
)

print(resp2.content)

config1 = {'configurable':{'session_id':'Echo1234'}}
# 第三轮 : 返回的数据是流式的
for resp in do_msg.stream(
    {
        'yxy_msg':[HumanMessage(content='请给我讲讲撒野这本书')],
        'language':'English'
    } ,
    config = config1,
): print(resp.content , end='-')

config1 = {'configurable':{'session_id':'Echo1234'}}
# 第4轮
resp3 = do_msg.invoke(
    {
        'yxy_msg':[HumanMessage(content='请给我讲讲撒野这本书')],
        'language':'中文'
    } ,
    config = config1,
)

print(resp3.content)
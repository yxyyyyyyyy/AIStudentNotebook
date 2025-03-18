import os

from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langserve import add_routes

os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"
os.environ["LANGCHAIN_API_KEY"] = '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'

# 聊天机器人案例
# 创建模型
model = ChatOpenAI(model='gpt-4-turbo')

# 准备测试数据 ，假设我们提供的文档数据如下：
documents = [
    Document(
        page_content="狗是伟大的伴侣，以其忠诚和友好而闻名。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
    Document(
        page_content="猫是独立的宠物，通常喜欢自己的空间。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
    Document(
        page_content="金鱼是初学者的流行宠物，需要相对简单的护理。",
        metadata={"source": "鱼类宠物文档"},
    ),
    Document(
        page_content="鹦鹉是聪明的鸟类，能够模仿人类的语言。",
        metadata={"source": "鸟类宠物文档"},
    ),
    Document(
        page_content="兔子是社交动物，需要足够的空间跳跃。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
]

# 实例化一个向量数空间
vector_store = Chroma.from_documents(documents, embedding=OpenAIEmbeddings())
# 相似度的查询: 返回相似的分数， 分数越低相似度越高
# 检索器: bind(k=1) 返回相似度最高的第一个
retriever = RunnableLambda(vector_store.similarity_search).bind(k=1)

# 提示模板
message = """
使用提供的上下文仅回答这个问题:
{question}
上下文:
{context}
"""

prompt_temp = ChatPromptTemplate.from_messages([('human', message)])

# RunnablePassthrough允许我们将用户的问题之后再传递给prompt和model。
chain = {'question': RunnablePassthrough(), 'context': retriever} | prompt_temp | model

resp = chain.invoke('请介绍一下猫？')

print(resp.content)


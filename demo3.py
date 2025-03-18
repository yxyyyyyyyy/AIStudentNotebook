import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1080"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:1080"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo3"

# DeepSeek 兼容的 Embedding 模型
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-zh")  # 适用于中文

# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 准备测试数据 ，假设我们提供的文档数据如下：每个Document代表一个文档数据 , page_content是文本内容 , metadata是字典,键值对随意设置
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

# 实例化一个向量数据库
vector_store = Chroma.from_documents(documents, embedding=embedding_model)
# 相似度的查询: 返回相似的分数， 分数越低相似度越高
# print(vector_store.similarity_search_with_score("咖啡猫"))
# 根据向量空间得到一个检索器 这个检索器其实就是Runnable对象
retriever = RunnableLambda(vector_store.similarity_search).bind(k=1)
# print(retriever.batch(['咖啡猫', '鲨鱼']))

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
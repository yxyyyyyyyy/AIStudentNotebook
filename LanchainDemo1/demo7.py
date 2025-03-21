import datetime
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic.v1 import BaseModel, Field
from typing import Optional, List
import yt_dlp
import datetime
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# # 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo5"

# 🔹创建 OpenAI 代理（不传 `system_message`）
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)


# DeepSeek 兼容的 Embedding 模型
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-zh")  # 适用于中文

persist_dir = 'chroma_data_dir'  # 存放向量数据库的目录

# 加载磁盘中的向量数据库
vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
result = vectorstore.similarity_search_with_score('How can we build an agent of RAG?')
# print(result[0])
# print(result[0][0].metadata['publish_year'])

system = """You are an expert at converting user questions into database queries. \
You have access to a database of tutorial videos about a software library for building LLM-powered applications. \
Given a question, return a list of database queries optimized to retrieve the most relevant results.

If there are acronyms or words you are not familiar with, do not try to rephrase them."""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

# pydantic: 专门做数据管理的库
# 定义数据模型得到检索指令
class Search(BaseModel):
    """
    定义了一个数据模型
    """
    # 内容的相似性和发布年份
    query: str = Field(None, description='Similarity search query applied to video transcripts.')
    publish_year: Optional[int] = Field(None, description='Year video was published')

chain = {'question': RunnablePassthrough()} | prompt | model.with_structured_output(Search)

# resp1 = chain.invoke('how do I build a RAG agent?')
# print(resp1)
# resp2 = chain.invoke('videos on RAG published in 2023')
# print(resp2)

# 基于特定的值的搜索 - 根据检索条件去执行
def retrieval(search: Search) -> List[Document]:
    _filter = None
    if search.publish_year:
        # 根据publish_year，存在得到一个检索条件
        # "$eq"是Chroma向量数据库的固定语法
        _filter = {'publish_year': {"$eq": search.publish_year}}

    return vectorstore.similarity_search(search.query, filter=_filter)

new_chain = chain | retrieval

result = new_chain.invoke('videos on RAG published in 2023')
# result = new_chain.invoke('RAG tutorial')
print([(doc.metadata['title'], doc.metadata['publish_year']) for doc in result])


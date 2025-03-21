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

#  设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo5"

# 🔹创建 OpenAI 代理（不传 `system_message`）
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# pydantic: 处理数据，验证数据， 定义数据的格式， 虚拟化和反虚拟化，类型转换等等。

# 定义一个数据模型
class Person(BaseModel):
    """
    关于一个人的数据模型
    """
    name: Optional[str] = Field(default=None, description='表示人的名字')

    hair_color: Optional[str] = Field(
        default=None, description="如果知道的话，这个人的头发颜色"
    )
    height_in_meters: Optional[str] = Field(
        default=None, description="以米为单位测量的高度"
    )



class ManyPerson(BaseModel):
    """
    数据模型类： 代表多个人
    """
    people: List[Person]

# 定义自定义提示以提供指令和任何其他上下文。
# 1) 你可以在提示模板中添加示例以提高提取质量
# 2) 引入额外的参数以考虑上下文（例如，包括有关提取文本的文档的元数据。）
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个专业的提取算法。只从未结构化文本中提取相关信息。如果你不知道要提取的属性的值，返回该属性的值为null。",
        ),
        # 请参阅有关如何使用参考记录消息历史的案例
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

# with_structured_output 模型的输出是一个结构化的数据
chain = {'text': RunnablePassthrough()} | prompt | model.with_structured_output(schema=ManyPerson)

# text = '马路上走来一个女生，长长的黑头发披在肩上，大概1米7左右，'
text = "马路上走来一个女生，长长的黑头发披在肩上，大概1米7左右。走在她旁边的是她的男朋友，叫：刘海；比她高10厘米。"
# text = "My name is Jeff, my hair is black and i am 6 feet tall. Anna has the same color hair as me."
resp = chain.invoke(text)
print(resp)
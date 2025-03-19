from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
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


import yt_dlp
# 🔹创建 OpenAI 代理（不传 `system_message`）
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)


# DeepSeek 兼容的 Embedding 模型
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-zh")  # 适用于中文

persist_dir = 'chroma_data_dir1'  # 存放向量数据库的目录

# 一些YouTube的视频连接
urls = [
    "https://www.youtube.com/watch?v=dA1cHGACXCo",
    "https://www.youtube.com/watch?v=ZcEMLz27sL4",
    "https://www.youtube.com/watch?v=hvAPnpSfSGo",
    "https://www.youtube.com/watch?v=EhlPDL4QrWY",
    "https://www.youtube.com/watch?v=mmBo8nlu2j0",
    "https://www.youtube.com/watch?v=rQdibOsL1ps",
    "https://www.youtube.com/watch?v=28lC4fqukoc",
    "https://www.youtube.com/watch?v=es-9MgxB-uc",
    "https://www.youtube.com/watch?v=wLRHwKuKvOE",
    "https://www.youtube.com/watch?v=ObIltMaRJvY",
]

# 用于存储文档
docs = []


# 使用yt-dlp获取视频数据
def fetch_video_info(url):
    ydl_opts = {
        'format': 'bestaudio/best',  # 选择视频质量
        'extractaudio': True,  # 获取音频
        'writeinfojson': True,  # 提取视频信息
        'quiet': True,  # 禁止显示下载进度
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)  # 不下载视频，只提取信息
        subtitles = info_dict.get("subtitles", {})

        # 获取字幕（如果有）
        subtitle_text = ""
        if 'en' in subtitles:
            subtitle_text = "\n".join(subtitles['en'])

        # 如果没有字幕，就用视频标题
        if not subtitle_text:
            subtitle_text = info_dict.get("title", "")

        metadata = {
            "title": info_dict.get("title"),
            "publish_date": info_dict.get("upload_date"),
            "video_url": url,
            "subtitle_text": subtitle_text
        }

        # 创建文档
        doc = Document(
            page_content=subtitle_text,
            metadata=metadata
        )
        return doc


# 处理所有视频链接
for url in urls:
    docs.append(fetch_video_info(url))

# print(len(docs))
# print(docs[0].metadata)
# print(docs[0].page_content[:500])  # 第一个视频的字幕内容

# 给doc添加额外的元数据：视频发布的年份
for doc in docs:
    doc.metadata['publish_year'] = int(datetime.datetime.strptime(doc.metadata['publish_date'], '%Y%m%d').strftime('%Y'))

# 根据多个doc构建向量数据库
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=30)
split_doc = text_splitter.split_documents(docs)

# 向量数据库的持久化
vectorstore = Chroma.from_documents(split_doc, embedding_model, persist_directory='chroma_data_dir')
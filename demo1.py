# 案例一:Langchian实现LLM应用程序
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from langserve import add_routes

from scripts.regsetup import description

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1080"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:1080"

# 创建 OpenAI 客户端
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 定义提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ('system', '请将下面的内容翻译成{language}'),
    ('user', '{text}')
])

# 创建返回数据解析器
parser = StrOutputParser()

# 组合链
chain = prompt_template | model | parser

# 把程序部署成服务器
## 创建fastAPI的应用
app = FastAPI(title='我的Langchain服务',version='V1.0',description="使用Langchain翻译使用任何语句的服务器")

add_routes(
    app,
    chain,
    path='/chain'
)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='localhost', port=8000)




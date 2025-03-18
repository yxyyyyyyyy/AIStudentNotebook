import os

from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

os.environ['http_proxy'] = '127.0.0.1:7890'
os.environ['https_proxy'] = '127.0.0.1:7890'

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo"
os.environ["LANGCHAIN_API_KEY"] = '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'
# os.environ["TAVILY_API_KEY"] = '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'

# 创建模型
model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

# 加载我们的文档。我们将使用 WebBaseLoader 来加载博客文章：
loader = WebBaseLoader('https://lilianweng.github.io/posts/2023-06-23-agent/')
docs = loader.load()  # 得到整篇文章

# 第一种： Stuff

# Stuff的第一种写法
# chain = load_summarize_chain(model, chain_type='stuff')

# Stuff的第二种写法
# 定义提示
prompt_template = """针对下面的内容，写一个简洁的总结摘要:
"{text}"
简洁的总结摘要:"""
prompt = PromptTemplate.from_template(prompt_template)

llm_chain = LLMChain(llm=model, prompt=prompt)

stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name='text')

result = stuff_chain.invoke(docs)
print(result['output_text'])

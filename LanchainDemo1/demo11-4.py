import os

from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

# 设置代理（如果需要）
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["LANGCHAIN_PROJECT"] = "LangchainDemo3"
os.environ["TAVILY_API_KEY"] = "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"


# 创建模型
model = ChatOpenAI(
    openai_api_key="sk-84f2472c5c8042e0a23927b4176bdfe9",
    base_url="https://api.deepseek.com/v1",
    model_name="deepseek-chat"
)

# 加载我们的文档。我们将使用 WebBaseLoader 来加载博客文章：
loader = WebBaseLoader('https://lilianweng.github.io/posts/2023-06-23-agent/')
docs = loader.load()  # 得到整篇文章

'''
Refine: RefineDocumentsChain 类似于映射-归约：
细化文档链通过循环遍历输入文档并逐步更新其答案来构建响应。对于每个文档，它将当前文档和最新的中间答案传递给LLM链，以获得新的答案。
'''

# 定义提示
prompt_template = """针对下面的内容，写一个简洁的总结摘要:
"{text}"
简洁的总结摘要:"""
prompt = PromptTemplate.from_template(prompt_template)

refine_template = (
    "Your job is to produce a final summary\n"
    "We have provided an existing summary up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing summary"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "\n"
    "Given the new context, refine the original summary in Chinese"
    "If the context isn't useful, return the original summary."
)

# refine_template = (
#     "你的工作是做出一个最终的总结摘要。\n"
#     "我们提供了一个到某个点的现有摘要:{existing_answer}\n"
#     "我们有机会完善现有的摘要，基于下面更多的文本内容\n"
#     "------------\n"
#     "{text}\n"
#     "------------\n"
# )
refine_prompt = PromptTemplate.from_template(refine_template)

chain = load_summarize_chain(
    llm=model,
    chain_type="refine",
    question_prompt=prompt,
    refine_prompt=refine_prompt,
    return_intermediate_steps=False,
    input_key="input_documents",
    output_key="output_text",
)


text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000, chunk_overlap=0
)
split_docs = text_splitter.split_documents(docs)
result = chain.invoke({"input_documents": split_docs}, return_only_outputs=True)

print(result["output_text"])
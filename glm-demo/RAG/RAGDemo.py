import os

import lancedb
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import BaichuanTextEmbeddings
from langchain_community.vectorstores import LanceDB
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

os.environ['BAICHUAN_API_KEY'] = 'sk-732b2b80be7bd800cb3a1dbc330722b4'
loader = TextLoader('state_of_the_union.txt', encoding='utf8')

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False,
    separators=[
        "\n\n",
        "\n",
        ".",
        "?",
        "!",
        "。",
        "！",
        "？",
        ",",
        "，",
        " "
    ]
)

docs = text_splitter.split_documents(documents)
print('=======', len(docs))
embeddings = BaichuanTextEmbeddings()

# 连接向量数据库
connect = lancedb.connect(os.path.join(os.getcwd(), 'lanceDB'))  # 本地目录存储向量


vectorStore = LanceDB.from_documents(docs, embeddings, connection=connect, table_name='my_vectors')

query = '今年长三角铁路春游运输共经历多少天？'
# 测试一下向量数据库
# docs_and_score = vectorStore.similarity_search_with_score(query)
# for doc, score in docs_and_score:
#     print('-------------------------')
#     print('Score: ', score)
#     print("Content:  ", doc.page_content)


# 和大语言模型整合
retriever = vectorStore.as_retriever()
template = """Answer the question based only on the following context:
{context}
Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

# 创建模型
model = ChatOpenAI(
    model='glm-4-0520',
    api_key='0884a4262379e6b9e98d08be606f2192.TOaCwXTLNYo1GlRM',
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)

output_parser = StrOutputParser()

#  把检索器和用户输入的问题，结合得到检索结果
start_retriever = RunnableParallel({'context': retriever, 'question': RunnablePassthrough()})

# 创建长链
chain = start_retriever | prompt | model | output_parser

res = chain.invoke(query)
print(res)


from langchain_chroma import Chroma
from langchain_community.embeddings import ModelScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

# 创建模型
model = ChatOpenAI(
    model='glm-4-0520',
    temperature=0,
    api_key='bfa7f4a5ee344bedaf2f265018374987.leHBJXH7xDUZ9z41',
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)

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

# 如果未来我们采用国内大模型，相关的其他工具最好也是国内
# https://www.modelscope.cn/models/iic/nlp_gte_sentence-embedding_chinese-large/summary
# 在中文环境下推荐使用的Embeddings

embeddings = ModelScopeEmbeddings(model_id='iic/nlp_gte_sentence-embedding_chinese-base')

# 实例化一个向量数空间
vector_store = Chroma.from_documents(documents, embedding=embeddings)

# 相似度的查询: 返回相似的分数， 分数越低相似度越高
# print(vector_store.similarity_search_with_score('咖啡猫'))

# 检索器: bind(k=1) 返回相似度最高的第一个
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


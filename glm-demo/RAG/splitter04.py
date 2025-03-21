import os

from langchain_community.embeddings import BaichuanTextEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

with open('test.txt', encoding='utf8') as f:
    text_data = f.read()

os.environ['BAICHUAN_API_KEY'] = 'sk-732b2b80be7bd800cb3a1dbc330722b4'
embeddings = BaichuanTextEmbeddings()

text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type='percentile')

docs_list = text_splitter.create_documents([text_data])

print(docs_list[0].page_content)


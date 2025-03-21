import bs4
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(
    web_paths=('https://fastapi.tiangolo.com/zh/features/',),
    encoding='utf-8',
    bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=('md-content',)))
)

docs = loader.load()
print(docs)
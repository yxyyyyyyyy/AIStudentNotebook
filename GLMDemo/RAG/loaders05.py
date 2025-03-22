from langchain_community.document_loaders import PyPDFLoader

# loader = PyPDFLoader(file_path='test.pdf')
loader = PyPDFLoader(file_path='test.pdf', extract_images=True)

# 每一页对应一个document
data = loader.load()
print(data)
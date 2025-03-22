import os

from langchain_community.embeddings import BaichuanTextEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

with open('test.txt', encoding='utf8') as f:
    text_data = f.read()

os.environ['BAICHUAN_API_KEY'] = 'sk-d70fe5eb726a732522d1390388b434c3'
embeddings = BaichuanTextEmbeddings()

'''
百分位数（Percentile）
原理：计算句子间差异的百分位数，任何超过设定的X百分位的差异都会被视为分割点。
特点：这种方法侧重于根据数据的分布情况来确定分割点，适用于需要根据数据的整体分布来决定分割的场景。
'''
# text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type='percentile')
# docs_list = text_splitter.create_documents([text_data])
# print(docs_list[0].page_content)
'''
标准差（Standard Deviation）
原理：基于句子间差异的标准差来确定分割点。任何超过X标准差的差异都会导致分割。
特点：这种方法侧重于数据的波动程度，适用于需要根据数据的波动情况来决定分割点的场景。如果数据波动较大，分割点会更频繁。
'''
text_splitter1 = SemanticChunker(embeddings, breakpoint_threshold_type='standard_deviation')
docs_list1 = text_splitter1.create_documents([text_data])
print(docs_list1[0].page_content)


'''
四分位距（Interquartile Range, IQR）
原理：通过计算上四分位数（第75百分位数）与下四分位数（第25百分位数）之间的差值来得到四分位距。通常会将超过上四分位数加上一定倍数的IQR（或减去一定倍数的IQR）的数据点视为异常值，并以此作为分割点。
特点：这种方法可以帮助识别和分割那些在语义嵌入空间中显著不同的句子，从而在保持文本整体连贯性的同时，区分出显著不同的部分。
'''
# text_splitter2 = SemanticChunker(embeddings, breakpoint_threshold_type='interquartile')
# docs_list2 = text_splitter2.create_documents([text_data])
# print(docs_list2[0].page_content)



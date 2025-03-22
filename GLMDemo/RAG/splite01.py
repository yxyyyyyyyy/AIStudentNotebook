from langchain_text_splitters import RecursiveCharacterTextSplitter

with open('test.txt', encoding='utf8') as f:
    text_data = f.read()


'''
chunk_size：块的最大大小，其中大小由length_function决定
chunk_overlap：数据块之间的目标重叠。重叠数据块有助于在数据块之间划分上下文时减少信息丢失。
length_function：确定块大小的函数。
is_separator_regex：分隔符列表（默认为 ）是否应解释为正则表达式。
'''

# 递归切割器
# 默认的分隔符：["\n\n", "\n", " ", ""]
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, # 每一块最大的大小
    chunk_overlap=20, # 递归重叠的数量,可以允许的重叠的字符数量
    length_function=len, # 统计块的大小 按照字符数量,如果想以单词数量为大小,需要自己写函数
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

# chunks_list = text_splitter.split_documents([text_data]) #只能切document
chunks_list = text_splitter.create_documents([text_data]) # 可以接很长的字符串,也可以切割text_data

print(len(chunks_list))

print(chunks_list[0])
print('--------------------------')
print(chunks_list[1])

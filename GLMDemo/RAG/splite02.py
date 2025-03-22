from langchain_text_splitters import RecursiveCharacterTextSplitter, HTMLHeaderTextSplitter

html_string = """
<!DOCTYPE html>
<html>
<body>
    <div>
        <h1>Foo</h1>

        <p>Some intro text about Foo.</p>
        <div>
            <h2>Bar main section</h2>
            <p>Some intro text about Bar.</p>
            <h3>Bar subsection 1</h3>
            <p>Some text about the first subtopic of Bar.</p>
            <h3>Bar subsection 2</h3>
            <p>Some text about the second subtopic of Bar.</p>
        </div>
        <div>
            <h2>Baz</h2>
            <p>Some text about Baz</p>
        </div>
        <br>
        <p>Some concluding text about Foo</p>
    </div>
</body>
</html>
"""

label_split = [  # 定义章节的结构
    ('h1', '大章节 1'),
    ('h2', '小节 2'),
    ('h3', '章节中的小点 3'),
]

html_splitter = HTMLHeaderTextSplitter(label_split)

docs_list = html_splitter.split_text(html_string)

print('切割之后的结果: -------------------')
print(docs_list)


label_split_2 = [  # 定义章节的结构
    ('h1', '大章节'),
    ('h2', '小节'),
    ('h3', '章节中的小点'),
    ('h4', '小点中的子节点'),
]
html_splitter = HTMLHeaderTextSplitter(label_split_2)

docs_list = html_splitter.split_text_from_url('https://plato.stanford.edu/entries/goedel/')

print(docs_list[0])

print('--------------------')
print('总共有多少个docs： ', len(docs_list))
print('--------------------------------')
print(docs_list[1])

# 由于章节的内容太多，可以切两次


# 默认的分隔符：["\n\n", "\n", " ", ""]
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=20,
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

docs2_list = text_splitter.split_documents(docs_list)
print('---------------------------------')
print(len(docs2_list))
print('---------------------------------')
print(docs2_list[1])

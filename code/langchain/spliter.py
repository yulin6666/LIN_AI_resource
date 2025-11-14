from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

loader = TextLoader('files/计算机技术与软件专业技术资格（水平）考试简介.txt',encoding='utf-8')
docs=loader.load()

#CharacterTextSplitter
text_splitter=CharacterTextSplitter(
    separator="",   # 没有分割符，也就是连贯分割
    chunk_size=200,      # 文本块的大小
    chunk_overlap=20,  # 重叠部分的大小
    length_function=len,
)
texts=text_splitter.create_documents([docs[0].page_content])
# print(len(texts))
# for i in texts:
#     print(i)
#     print('--')

# 实例化文本分割器
text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True,
    separators=["\n\n", "\n", " ", ""] 
)
texts = text_splitter.create_documents([docs[0].page_content])
# print(len(texts))
# for i in texts:
#     print(i)
#     print('--')

# html分割器
from langchain_text_splitters import HTMLHeaderTextSplitter
html_string = """
<html>
    <body>
        <h1>主标题</h1>
        <p>这是主标题下的内容</p>
        <h2>子标题1</h2>
        <p>这是子标题1下的内容</p>
        <h3>子子标题</h3>
        <p>这是子子标题下的内容</p>
        <h2>子标题2</h2>
        <p>这是子标题2下的内容</p>
    </body>
</html>
"""
headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]
splitter = HTMLHeaderTextSplitter(
 headers_to_split_on=headers_to_split_on
)
html_header_splits = splitter.split_text(html_string)
# for split in html_header_splits:
#     print(split)
#     print("---")

#markdown分割器
from langchain_text_splitters import MarkdownHeaderTextSplitter
Markdown_document="""# 第一章\n\n这是第一章的内容\n\n## 第一节\n\n这是第一节的内容\n\n### 第一小节\n\n这是第一小节的内容"""
header_to_splitter_on=[
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
markdown_splitter=MarkdownHeaderTextSplitter(header_to_splitter_on)
md_header_splits=markdown_splitter.split_text(Markdown_document)
for i in docs:
    print(i)

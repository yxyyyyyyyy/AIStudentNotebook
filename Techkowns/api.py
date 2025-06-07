from fastapi import FastAPI, Query as FastQuery
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

app = FastAPI()

model = SentenceTransformer('all-MiniLM-L6-v2')

# 载入文本库
with open("knowledge_base.txt", "r", encoding="utf-8") as f:
    corpus = [line.strip() for line in f if line.strip()]

# 索引文件路径
index_path = "faiss.index"
corpus_path = "corpus.txt"

if os.path.exists(index_path) and os.path.exists(corpus_path):
    # 如果索引和文本已存在，直接加载
    index = faiss.read_index(index_path)
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = [line.strip() for line in f]
else:
    # 没有索引，则encode文本生成向量，创建索引
    doc_embeddings = model.encode(corpus, normalize_embeddings=True)
    doc_embeddings = np.array(doc_embeddings).astype('float32')

    dimension = doc_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(doc_embeddings)

    # 保存索引和文本文件，方便下次加载
    faiss.write_index(index, index_path)
    with open(corpus_path, "w", encoding="utf-8") as f:
        for line in corpus:
            f.write(line + "\n")

@app.get("/search_v2")
def search(
    question: str = FastQuery(..., description="查询内容"),
    top_k: int = FastQuery(1, description="返回Top K条结果"),
    min_score: float = FastQuery(0.3, description="余弦相似度阈值，默认0.3")
):
    q_emb = model.encode([question], normalize_embeddings=True).astype('float32')
    D, I = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if score >= min_score:
            results.append({"text": corpus[idx], "score": float(score)})

    return {"results": results}

# 本地知识库-利用分割文本向量模型对本地文本文件操作建立向量知识库进行搜索
from fastapi import FastAPI, Query as FastQuery
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = FastAPI()

model = SentenceTransformer('all-MiniLM-L6-v2')

with open("corpus.txt", "r", encoding="utf-8") as f:
    corpus = [line.strip() for line in f if line.strip()]

index = faiss.read_index("faiss.index")

@app.get("/search_v3")
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

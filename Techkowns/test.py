from sentence_transformers import SentenceTransformer
import numpy as np

# 加载模型
model = SentenceTransformer('all-MiniLM-L6-v2')

# 读语料库
with open("knowledge_base.txt", "r", encoding="utf-8") as f:
    corpus = [line.strip() for line in f if line.strip()]

# 编码并归一化
embeddings = model.encode(corpus, normalize_embeddings=True)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2)

def test_similarity(query):
    q_emb = model.encode([query], normalize_embeddings=True)[0]
    print(f"测试问题：{query}\n")

    scores = []
    for idx, sent_emb in enumerate(embeddings):
        score = cosine_similarity(q_emb, sent_emb)
        scores.append((score, corpus[idx]))

    # 按相似度降序排序
    scores = sorted(scores, key=lambda x: x[0], reverse=True)

    print(f"语料相似度 Top 10:")
    for score, text in scores[:10]:
        print(f"相似度: {score:.4f}  句子: {text}")

if __name__ == "__main__":
    test_queries = [
        "苦难",
        "撒野",
    ]
    for q in test_queries:
        test_similarity(q)
        print("\n" + "-"*50 + "\n")

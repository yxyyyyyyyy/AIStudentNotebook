import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json

model = SentenceTransformer("./local_sentence_transformer_model")

kb_path = "./knowledge_base.txt"
index_path = "./kb.index"
meta_path = "kb_meta.json"

questions = []
answers = []

with open(kb_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if "|" not in line:
            print(f"跳过无效行: {line}")
            continue
        q, a = line.split("|", 1)
        questions.append(q)
        answers.append(a)

print(f"共读取 {len(questions)} 条问答。")
if len(questions) == 0:
    print("错误：未读取到任何问答，请检查 knowledge.txt 文件格式和路径。")
    exit(1)


# 编码为向量
embeddings = model.encode(questions, convert_to_numpy=True, normalize_embeddings=True).astype("float32")

# 若为一维则 reshape
if len(embeddings.shape) != 2:
    embeddings = embeddings.reshape(-1, embeddings.shape[-1])

# 构建 FAISS 索引
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# 保存索引
faiss.write_index(index, index_path)

# 保存映射信息
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump({"questions": questions, "answers": answers}, f, ensure_ascii=False, indent=2)

print("✅ 向量数据库构建完成。")

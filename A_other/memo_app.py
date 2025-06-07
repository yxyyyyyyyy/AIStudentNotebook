from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
from datetime import datetime

MEMO_FILE = "memos.json"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

def load_memos():
    if not os.path.exists(MEMO_FILE):
        return []
    try:
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_memos(memos):
    with open(MEMO_FILE, "w", encoding="utf-8") as f:
        json.dump(memos, f, ensure_ascii=False, indent=2)

class MemoItem(BaseModel):
    content: str

@app.get("/memos")
def get_memos():
    return load_memos()

@app.post("/memos")
def add_memo(item: MemoItem):
    memos = load_memos()
    memos.append({
        "content": item.content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_memos(memos)
    return {"success": True, "message": "备忘录添加成功"}

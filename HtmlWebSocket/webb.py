from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import os
from datetime import datetime
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = FastAPI()
MEMO_FILE = "memos.json"
connected_clients: List[WebSocket] = []

def load_memos():
    if not os.path.exists(MEMO_FILE):
        return []
    with open(MEMO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def broadcast_memos():
    memos = load_memos()
    data = json.dumps(memos, ensure_ascii=False)
    disconnected = []
    for ws in connected_clients:
        try:
            await ws.send_text(data)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        connected_clients.remove(ws)

@app.websocket("/ws/memos")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    # 新连接时先推送一次当前数据
    await broadcast_memos()
    try:
        while True:
            # 维持连接，内容可忽略
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# 文件变更监听器
class MemoFileHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop

    def on_modified(self, event):
        if event.src_path.endswith(MEMO_FILE):
            # 通过线程安全方式调用异步广播
            asyncio.run_coroutine_threadsafe(broadcast_memos(), self.loop)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    event_handler = MemoFileHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    app.state.observer = observer

@app.on_event("shutdown")
def shutdown_event():
    observer = app.state.observer
    observer.stop()
    observer.join()

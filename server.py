# server.py
# Author: Tom
# 2025/12/15 Update with command shell

# source venv/bin/activate
# python3 server.py

# create command shell -> chmod +x run_server.command

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import socket

app = FastAPI()


# Absolute path to the static folder
current_dir = os.path.dirname(__file__)
# 提供静态文件
app.mount("/static", StaticFiles(directory=current_dir), name="static")

# HTML frontend serving
@app.get("/")
async def get_index():
    return FileResponse(os.path.join(current_dir, "index.html"))

clients = set()
document_text = ""  # 存储文档内容

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    global document_text

    await ws.accept()
    clients.add(ws)
    print(f"Client connected: {ws.client}")
    await ws.send_text(document_text)  # 发送当前文档内容给新连接的客户端
    try:
        while True:
            data = await ws.receive_text()
            document_text = data  # update server state
            # 广播给所有客户端
            for client in clients.copy():
                if client != ws:
                    try:    
                        await client.send_text(data)
                    except:
                        clients.remove(client)
    except WebSocketDisconnect:
        clients.remove(ws)
        print(f"Client disconnected: {ws.client}")


# Utility function to get LAN IP
def get_lan_ip():
    """Detect the LAN IP of this machine"""
    try:
        # Connect to an external host, doesn't actually send data
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "clients": len(clients)}


@app.get("/server-info")
def server_info():
    lan_ip = get_lan_ip()
    return {"lan_ip": lan_ip, "port": 8000}

# Run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

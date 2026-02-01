import asyncio
import ssl
import websockets
from fastapi import FastAPI, Body, HTTPException,Header
import uvicorn
from typing import Optional
from websockets.protocol import State
# --- 配置区 ---
VALID_TOKEN = "token-server2pc"
VALID_TOKEN2= "token-front2server"#input in front web
pc_connection: Optional[websockets.WebSocketServerProtocol] = None

app = FastAPI()

# --- 1. WebSocket 逻辑 ---
async def ws_handler(websocket):
    global pc_connection
    auth_msg = await websocket.recv()
    if auth_msg == f"TOKEN:{VALID_TOKEN}":
        await websocket.send("认证成功")
        pc_connection = websocket
        print("✅ PC 已上线")
        try:
            await websocket.wait_closed()
        finally:
            pc_connection = None
            print("❌ PC 已下线")
    else:
        await websocket.close()

# --- 2. HTTP 接口 ---
@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/send_to_pc")
async def send_to_pc(
    content: str = Body(..., embed=True),
    x_token: str = Header(None)
):
    # 1. 验证 Token (保持不变)
    if x_token != VALID_TOKEN2:
        raise HTTPException(status_code=403, detail="Invalid API Token")

    # 2. 检查 PC 在线状态
    if not pc_connection or pc_connection.state.name != "OPEN":
        # 模仿 Gemini 的错误结构或空返回
        return {
            "candidates": [{
                "content": {"parts": [{"text": "错误: PC 离线"}], "role": "model"},
                "finishReason": "STOP",
                "index": 0
            }],
            "model": "none"
        }
    
    # 3. 转发并等待
    await pc_connection.send(content)
    try:
        reply = await asyncio.wait_for(pc_connection.recv(), timeout=120.0)
        
        # --- 核心：模仿 Gemini 官方格式 ---
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": reply}
                        ],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0,
                    "safetyRatings": [] # 可根据需要填入
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 0,
                "candidatesTokenCount": 0,
                "totalTokenCount": 0
            },
            "model": "none"  # 你的需求：没有对应 model 则填 none
        }
        
    except asyncio.TimeoutError:
        return {
            "candidates": [{
                "content": {"parts": [{"text": "错误: PC 响应超时"}], "role": "model"},
                "finishReason": "MAX_TOKENS"
            }],
            "model": "none"
        }
    except Exception as e:
        return {"error": {"code": 500, "message": str(e), "status": "INTERNAL"}}
# --- 3. 核心启动逻辑 ---
async def start_all():
    # A. 启动 WebSocket (非阻塞)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="your_bundle.pem", keyfile="your.key")
    
    # 启动 WSS 监听
    ws_server = await websockets.serve(ws_handler, "0.0.0.0", 8765, ssl=ssl_context)
    print("🛰️  WSS 服务启动在 8765")

    # B. 启动 FastAPI
    # 我们不直接用 uvicorn.run，因为那是同步的。我们手动配置 Server 并启动。
    config = uvicorn.Config(app, host="0.0.0.0", port=443, log_level="info",ssl_keyfile="xinyava.xyz.key",    # 确保文件就在当前目录
        ssl_certfile="xinyava.xyz_bundle.pem",
        ssl_version=ssl.PROTOCOL_TLS_SERVER)
    server = uvicorn.Server(config)
    
    print("🚀 HTTP 服务启动在 443")
    await server.serve()

if __name__ == "__main__":
    # 用 asyncio.run 运行这个复合函数
    try:
        asyncio.run(start_all())
    except KeyboardInterrupt:
        pass
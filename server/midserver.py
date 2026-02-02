import asyncio
import ssl
import websockets
from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# --- 1. 配置区 ---
VALID_TOKEN_PC = "token-server2pc"   # PC 连接 WebSocket 使用的 Token
VALID_API_KEY = "token-front2server"    # 你在 curl 或工具中填入的 API Key
pc_connection: Optional[websockets.WebSocketServerProtocol] = None

# --- 2. 官方数据模型 ---
class GeminiPart(BaseModel):
    text: str

class GeminiContent(BaseModel):
    parts: List[GeminiPart]
    role: Optional[str] = "user"

class GeminiRequest(BaseModel):
    contents: List[GeminiContent]

app = FastAPI()

# --- 3. WebSocket 逻辑 ---
async def ws_handler(websocket):
    global pc_connection
    try:
        auth_msg = await websocket.recv()
        if auth_msg == f"TOKEN:{VALID_TOKEN_PC}":
            await websocket.send("认证成功")
            pc_connection = websocket
            print("✅ PC 已上线")
            await websocket.wait_closed()
    finally:
        pc_connection = None
        print("❌ PC 已下线")

# --- 4. 核心接口：对齐官网路径与 Header ---
# 兼容：/v1beta/models/gemini-3-flash-preview:generateContent 等所有模型路径
@app.post("/v1beta/models/{model_name}:generateContent")
@app.post("/send_to_pc") # 保留你的旧路径
async def handle_gemini_request(
    request_data: GeminiRequest,
    model_name: str = "none",
    x_goog_api_key: Optional[str] = Header(None), # 官方标准 Header
    key: Optional[str] = Query(None),              # 官方标准 URL 参数
    x_token: Optional[str] = Header(None)          # 你之前的自定义 Header
):
    # 鉴权：自动检查官方 Header、URL 参数或自定义 Header
    token = x_goog_api_key or key or x_token
    
    if token != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")

    # 提取纯文本指令
    try:
        user_command = request_data.contents[-1].parts[0].text
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid Gemini JSON structure")

    # 检查 PC 是否在线
    if not pc_connection or pc_connection.state.name != "OPEN":
        return {
            "candidates": [{
                "content": {"parts": [{"text": "错误: PC 离线中"}], "role": "model"},
                "finishReason": "STOP",
                "index": 0
            }],
            "model": "none"
            
        }
    
    # 转发给 PC 并等待返回
    try:
        await pc_connection.send(user_command)
        reply = await asyncio.wait_for(pc_connection.recv(), timeout=180.0)
        
        # 返回标准的官网响应格式
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": reply}],
                        "role": "model"
                    },
                    "finishReason": "STOP",
                    "index": 0,
                    "safetyRatings": [] # 可根据需要填入
                }
            ],
            "usageMetadata": {
                "promptTokenCount": len(user_command),
                "candidatesTokenCount": len(reply),
                "totalTokenCount": len(user_command) + len(reply)
            },
            
            "model": "none"
        }
    except asyncio.TimeoutError:
        return {"candidates": [{"content": {"parts": [{"text": "错误: PC 响应超时"}]}, "finishReason": "MAX_TOKENS"}]}

# --- 5. 启动逻辑 ---
async def start_services():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="xinyava.xyz_bundle.pem", keyfile="xinyava.xyz.key")
    
    # 启动 WebSocket
    await websockets.serve(ws_handler, "0.0.0.0", 8765, ssl=ssl_context)
    print("🛰️  WSS 服务启动在 8765")

    # 启动 HTTPS FastAPI
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=443, 
        ssl_keyfile="xinyava.xyz.key", 
        ssl_certfile="xinyava.xyz_bundle.pem"
    )
    server = uvicorn.Server(config)
    print("🚀 HTTPS 服务已启动，完全兼容官网 API 路径")
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass

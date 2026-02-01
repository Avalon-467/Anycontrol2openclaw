# import asyncio
# import websockets
# import ssl

# async def get_authenticated_ws():
#     uri = "wss://124.156.204.237:8765"
#     token = "token-server2pc"

#     # 配置 SSL
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#     ssl_context.load_verify_locations("server.crt")

#     # --- 关键改变：不再使用 async with ---
#     print(f"正在连接到 {uri}...")
#     websocket = await websockets.connect(uri, ssl=ssl_context)
    
#     try:
#         # 1. 发送 Token 进行验证
#         await websocket.send(f"TOKEN:{token}")
#         auth_res = await websocket.recv()
#         print(f"服务器回应: {auth_res}")

#         if "成功" in auth_res:
#             return websocket  # 认证成功，直接返回该连接对象
#         else:
#             await websocket.close()
#             return None
            
#     except Exception as e:
#         print(f"验证过程中出错: {e}")
#         await websocket.close()
#         return None

# async def listen_loop(websocket):
#     """专门负责监听的函数"""
#     print("正在监听指令...")
#     try:
#         async for message in websocket:
#             print(f"\n[收到新指令]: {message}")
#             await websocket.send(f"已收到并打印: {message}")
#     except websockets.ConnectionClosed:
#         print("连接已关闭")

# async def main():
#     # 获取连接
#     ws = await get_authenticated_ws()
    
#     if ws:
#         try:
#             # 你现在可以自由地把 ws 传给其他函数使用
#             await listen_loop(ws)
#         finally:
#             # --- 必须手动关闭 ---
#             print("正在关闭连接...")
#             await ws.close()
#     else:
#         print("认证失败，程序退出")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("停止客户端")


import asyncio
import websockets
import ssl
import subprocess

# --- AI 调用函数 ---
def ask_ai(question: str) -> str:
    """通过 OpenClaw 调用 AI，返回回答"""
    try:
        # 调用 OpenClaw CLI，指定使用 main 代理
        result = subprocess.run(
            ['openclaw', 'agent', '--agent', 'main', '--message', question],
            capture_output=True,
            text=True,
            timeout=120  # AI 回复较慢，给 60 秒时间
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"AI 运行出错: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "错误: AI 响应超时"
    except Exception as e:
        return f"错误: {str(e)}"

# --- WebSocket 连接逻辑 ---
async def get_authenticated_ws():
    uri = "wss://www.xinyava.xyz:8765"
    token = "token-server2pc"

    # 配置 SSL
    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #ssl_context.load_verify_locations(cafile="ca_bundle.crt")  # CA 根证书或中间证书
    ssl_context = ssl.create_default_context()


    print(f"正在连接到 {uri}...")
    try:
        websocket = await websockets.connect(uri, ssl=ssl_context)
        # 1. 发送 Token 进行验证
        await websocket.send(f"TOKEN:{token}")
        auth_res = await websocket.recv()
        print(f"服务器回应: {auth_res}")

        if "成功" in auth_res:
            return websocket
        else:
            await websocket.close()
            return None
    except Exception as e:
        print(f"连接失败: {e}")
        return None

# --- 核心监听逻辑 ---
async def listen_loop(websocket):
    """负责监听指令并调用 AI 回答"""
    print("🤖 AI 助手已就绪，正在监听远程指令...")
    try:
        async for message in websocket:
            print(f"\n[收到手机指令]: {message}")
            
            # 使用 to_thread 运行同步的 ask_ai，避免卡死网络循环
            print("🧠 AI 正在思考中...")
            reply = await asyncio.to_thread(ask_ai, message)
            
            # 将 AI 的回答发送回云端，最终传给手机
            await websocket.send(str(reply))
            print(f"✅ 已回传 AI 回复: {reply[:50]}...")
            
    except websockets.ConnectionClosed:
        print("❌ 连接已关闭")

async def main():
    ws = await get_authenticated_ws()
    if ws:
        try:
            await listen_loop(ws)
        finally:
            print("正在关闭连接...")
            await ws.close()
    else:
        print("认证失败，程序退出")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n停止客户端")
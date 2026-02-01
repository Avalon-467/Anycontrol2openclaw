from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# --- 配置区 ---
# 指向你的 FastAPI Midserver 地址
BRIDGE_URL = "https://127.0.0.1:443/send_to_pc"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>xiny anycontrol</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.2/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>

    <style>
        /* 1. 风格变量系统 */
        :root {
            --bg-color: #f0f2f5;
            --container-bg: #ffffff;
            --text-main: #1c1e21;
            --accent: #0084ff;
            --border: #dddfe2;
            --msg-ai: #f0f2f5;
        }

        body.style-chat { --bg-color: #e5ddd5; }
        body.style-doc { --bg-color: #ffffff; --container-bg: #f9f9f9; --text-main: #333333; --border: #eeeeee; }
        body.style-terminal { 
            --bg-color: #0d0d0d; 
            --container-bg: #1a1a1a; 
            --text-main: #00ff41; 
            --accent: #00ff41; 
            --border: #00ff41; 
            --msg-ai: #1a1a1a; 
        }

        @media (prefers-color-scheme: dark) {
            body.style-chat:not(.forced) {
                --bg-color: #0b141a;
                --container-bg: #212c33;
                --text-main: #e9edef;
                --border: #3b4a54;
                --msg-ai: #202c33;
            }
        }

        /* 2. 基础布局 */
        body { transition: 0.3s; background: var(--bg-color); color: var(--text-main); font-family: sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
        #header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        #chat-container { 
            background: var(--container-bg); border: 1px solid var(--border); 
            height: 65vh; overflow-y: auto; padding: 20px; border-radius: 12px; 
            display: flex; flex-direction: column; gap: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .message { padding: 12px 16px; border-radius: 12px; max-width: 85%; line-height: 1.6; word-wrap: break-word; }
        .user { align-self: flex-end; background: var(--accent); color: white; border-bottom-right-radius: 2px; }
        .ai { align-self: flex-start; background: var(--msg-ai); border: 1px solid var(--border); border-bottom-left-radius: 2px; }

        /* Markdown 样式 */
        .markdown-body pre { background: #1e1e1e; padding: 12px; border-radius: 8px; overflow-x: auto; margin: 10px 0; border: 1px solid #444; }
        .markdown-body code { font-family: 'Consolas', monospace; font-size: 0.9em; }
        .style-terminal .message { border-radius: 0 !important; border: 1px solid var(--accent) !important; }

        .controls { margin-top: 20px; display: flex; flex-direction: column; gap: 10px; }
        input, select { background: var(--container-bg); border: 1px solid var(--border); color: var(--text-main); padding: 12px; border-radius: 8px; outline: none; }
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .btn-send { background: var(--accent); color: white; }
        .btn-clear { background: #ff4d4f; color: white; }

        /* 动画 */
        .typing { display: flex; gap: 6px; padding: 15px !important; align-items: center; }
        .dot { width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.2); } }
    </style>
</head>
<body class="style-chat">
    <div id="header">
        <h2 style="margin:0;">xiny anycontrol</h2>
        <div style="display:flex; gap:10px;">
            <select onchange="document.body.className=this.value">
                <option value="style-chat">对话风格</option>
                <option value="style-doc">文档风格</option>
                <option value="style-terminal">终端风格</option>
            </select>
            <button class="btn btn-clear" onclick="clearChat()">清空对话</button>
        </div>
    </div>

    <input type="password" id="token" placeholder="输入身份token" style="width: 100%; box-sizing: border-box; margin-bottom: 10px;">
    <div id="chat-container"><div class="message ai">准备连接agent</div></div>

    <div class="controls">
        <div style="display:flex; gap:10px;">
            <input type="text" id="question" placeholder="输入指令..." style="flex:1" onkeypress="if(event.keyCode==13) ask()">
            <button class="btn btn-send" id="send-btn" onclick="ask()">发送</button>
        </div>
    </div>

    <script>
        // 1. 初始化 Marked 配置
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                highlight: function(code, lang) {
                    if (typeof hljs !== 'undefined') {
                        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                        return hljs.highlight(code, { language }).value;
                    }
                    return code;
                },
                langPrefix: 'hljs language-'
            });
        }

        async function clearChat() {
            const token = document.getElementById("token").value.trim();
            if(!token) return alert("请先输入 Token");
            const res = await fetch("/proxy_ask", {
                method: "POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({token, content: "开启新话题"})
            });
            document.getElementById("chat-container").innerHTML = '<div class="message ai">准备连接agent</div>';
        }

        async function ask() {
            const token = document.getElementById("token").value.trim();
            const qInput = document.getElementById("question");
            const btn = document.getElementById("send-btn");
            const container = document.getElementById("chat-container");
            const text = qInput.value.trim();

            if (!text || !token) return;

            qInput.value = "";
            btn.disabled = true;
            container.innerHTML += `<div class="message user">${text}</div>`;
            const tid = "t-" + Date.now();
            container.innerHTML += `<div class="message ai typing" id="${tid}"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
            container.scrollTop = container.scrollHeight;

            try {
                const res = await fetch("/proxy_ask", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token, content: text })
                });
                const data = await res.json();
                const node = document.getElementById(tid);

                let rawText = "";
                if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
                    rawText = data.candidates[0].content.parts[0].text;
                } else {
                    rawText = data.reply || data.detail || JSON.stringify(data);
                }

                if(node) {
                    node.classList.remove('typing');
                    // 检查库加载情况，防止报错
                    const htmlContent = (typeof marked !== 'undefined') ? marked.parse(rawText) : rawText;
                    node.innerHTML = `<b>Agent:</b><br><div class="markdown-body">${htmlContent}</div>`;
                    
                    if (typeof hljs !== 'undefined') {
                        node.querySelectorAll('pre code').forEach((el) => { hljs.highlightElement(el); });
                    }
                }
            } catch (e) {
                const node = document.getElementById(tid);
                if(node) node.innerHTML = "❌ 渲染失败: " + e.message;
            }
            btn.disabled = false;
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/proxy_ask", methods=["POST"])
def proxy_ask():
    data = request.json
    try:
        headers = {"X-Token": data.get("token"), "Content-Type": "application/json"}
        # 增加超时时间，verify=False 忽略证书校验
        r = requests.post(BRIDGE_URL, json={"content": data.get("content")}, headers=headers, verify=False, timeout=120)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, ssl_context=("xinyava.xyz_bundle.pem", "xinyava.xyz.key"))
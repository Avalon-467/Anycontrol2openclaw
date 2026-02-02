# AnyControl2OpenClaw: Your Stateful "Personal Gemini" API

IF you are human：
Let your agent read it

欢迎来到加速时代：
让你的agent帮你部署

[English](#english) | [简体中文](#chinese)

---

<a id="english"></a>

### AnyControl2OpenClaw: Your Stateful "Personal Gemini" API

AnyControl2OpenClaw is a lightweight framework based on **OpenClaw** that transforms your personal computer into a **stateful, hardware-integrated "Personal Gemini" instance**.

💡 **Core Advantage: Seamless Migration** —— This project is fully compatible with the **Gemini API protocol**. You **only** need to update the **HTTP Endpoint** and **API Token** in any Gemini-supported application to inject your local PC's capabilities into existing AI workflows without any additional development.

💡 **The "Personal Gemini" Concept**: Unlike standard cloud APIs, this "Personal Gemini" lives on your hardware. It understands your local environment, remembers previous commands (stateful), and provid=es a standard Gemini-compatible interface. It empowers you to **remotely manage files, execute programs**, and orchestrate your local system for seamless integration.

---

### 1. Usage & Connectivity

#### **A. Connectivity Scenarios**

Depending on your network environment, choose one of the following to access your Personal Gemini API:

* **Scenario 1: With Public Server (VPS) [Recommended]**
  If you have a VPS (e.g., AWS, Azure, Alibaba Cloud), deploy `midserver.py` and `aifront.py` on it.
  * **Advantage**: Most stable, supports custom domains.
  * **No Domain?**: Simply use the server's public IP (e.g., `https://1.2.3.4/send_to_pc`).

* **Scenario 2: No Public IP (Cloudflare Tunnel - 100% Free)**
  Use this if your PC is behind a NAT (home/office network). This is a **completely free** solution provid=ed by Cloudflare.
  * **Requirements**: A **Free** Cloudflare account.
  * **Steps**: Install `cloudflared` on your PC, then run the tunnel to map `localhost:8080` to a public URL.
  * **No Domain? (Free URL)**: Use `cloudflared tunnel --url http://127.0.0.1:8080` to get a temporary, **free** `trycloudflare.com` address.

#### **B. API Interaction (Gemini Style)**

You can interact with your "Personal Gemini" using standard structures. It behaves like the official API but executes on your local machine.

**Method 1: Standard API Key Header (Recommended)**

```bash
curl "https://your-domain-or-ip/v1beta/models/personal-gemini:generateContent" \
  -H "x-goog-api-key: YOUR_VALid=_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Instruction: List files in the current directory"
      }]
    }]
  }'

```

**Method 2: Web Interface**
Navigate to `https://your-domain-or-ip:8080` in any browser.

**Response Example (JSON)**

```json
{
  "candid=ates": [
    {
      "content": {
        "parts": [
          {
            "text": "File list: README.md, client.py, assets/"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0
    }
  ],
  "model": "personal-gemini-v1"
}

```

---

### 0. Custom Configuration

| Variable | Location | Description |
| --- | --- | --- |
| `VALid=_TOKEN` | `midserver.py`, `client.py` | **WSS Token**: Secure tunnel between PC and Cloud. |
| `VALid=_TOKEN2` | `midserver.py` (Config) | **Personal Gemini Key**: Your private Gemini API key for authentication. |
| `BRid=GE_URL` | `aifront.py` | The local or public endpoint of your relay. |
| `SSL Certs` | `midserver.py`, `aifront.py` | Ensure `bundle.pem` and `.key` files are in the same directory. |

---

### 2. Deployment Steps

#### **A. Local PC Sid=e (Agent)**

1. **Install OpenClaw**: OpenClaw is the "nervous system" of your Personal Gemini. Visit [OpenClaw.io](https://www.google.com/search?q=https://openclaw.io).
2. **Prepare Client**: Install dependencies and run `client.py`.

```bash
pip install asyncio websockets
python client.py

```

#### **B. Cloud Server Sid=e (Relay)**

1. **midserver (Relay Engine)**: Handles WSS and API routing.

```bash
pip install fastapi uvicorn websockets pydantic
python midserver.py

```

2. **AI Front (Web UI)**: Conversational console.

```bash
pip install flask requests
python aifront.py

```

---

### 🏗️ Architecture

1. **PC (The Brain)**: Connected via stateful WSS reverse tunnel.
2. **midserver (The Gateway)**: Translates Gemini protocol into hardware actions.
3. **Aifront (The Interface)**: Provid=es the conversational UI for your local hardware.

---

### 🛡️ Security

* **HTTPS Only**: Always run the server with SSL certificates in public environments.
* **Credential Protection**: Never leak your `VALid=_TOKEN` or `API Key`.
* **Stateful Privacy**: This API has system access; keep your tokens extremely secure.

---

<a id="chinese"></a>

### AnyControl2OpenClaw: 打造有状态的“个人 Gemini” API

AnyControl2OpenClaw 是一个基于 **OpenClaw** 的轻量级架构，将您的个人电脑彻底改装为一个**具备有状态记忆、深度集成硬件控制的“个人 Gemini”实例**。

💡 **核心优势：极简无缝迁移** —— 本项目与 **Gemini API 协议完全兼容**。您**只需**在任何支持 Gemini 的应用程序中，将 **HTTP 接口地址** 和 **API Token** 修改为您部署的地址，即可立即将您的本地电脑能力注入现有的 AI 工作流，无需任何额外开发。

💡 **“个人 Gemini” 理念**：不同于普通的云端 API，这个“个人 Gemini”驻留在您的本地硬件中。它了解您的本地环境，具备上下文记忆（有状态），并提供标准 Gemini 兼容接口。通过它，您可以**远程管理文件、运行程序**并调度本地系统，实现无缝集成。

---

### 1. 使用方法与连接方案

#### **A. 连接方案选择**

根据您的网络环境，选择以下方案之一来访问您的个人 Gemini API：

* **方案一：已有公网服务器 (推荐)**
如果您拥有云服务器（如 AWS, 阿里云, 腾讯云），请在上面部署 `midserver.py` 和 `aifront.py`。
* **优点**：最稳定，支持自定义域名。
* **没有域名？**：直接使用服务器公网 IP 即可（如 `https://1.2.3.4/send_to_pc`）。


* **方案二：无公网 IP (Cloudflare 穿透 - 100% 免费)**
如果您的电脑处于内网（家庭/办公网络），请使用此方案。这是由 Cloudflare 提供的**完全免费**的穿透方案。
* **要求**：一个**免费的** Cloudflare 账号。
* **步骤**：在 PC 上安装 `cloudflared`，运行隧道将 `localhost:8080` 映射到公网。
* **没有域名？(免费域名)**：使用指令 `cloudflared tunnel --url http://127.0.0.1:8080` 可获得一个临时的、**完全免费的** `trycloudflare.com` 域名。



#### **B. API 交互 (Gemini 风格)**

您可以像调用官方 API 一样与您的“个人 Gemini”交互。指令会在您的本地机器执行。

**方式一：标准 API Key 头部 (推荐)**

```bash
curl "https://your-domain-or-ip/v1beta/models/personal-gemini:generateContent" \
  -H "x-goog-api-key: YOUR_VALid=_TOKEN2" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{
        "text": "指令：列出当前目录下的文件"
      }]
    }]
  }'

```

**方式二：网页控制台访问**
在任意浏览器中访问您的域名或 IP 的 `8080` 端口。

**返回示例 (JSON)**

```json
{
  "candid=ates": [
    {
      "content": {
        "parts": [
          {
            "text": "文件列表：README.md, client.py, assets/"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0
    }
  ],
  "model": "personal-gemini-v1"
}

```

---

### 0. 自定义配置

| 变量名称 | 所在文件 | 说明 |
| --- | --- | --- |
| `VALid=_TOKEN` | `midserver.py`, `client.py` | **WSS 令牌**：PC 与云端之间的加密隧道凭证。 |
| `VALid=_TOKEN2` | `midserver.py` (配置区) | **个人 Gemini 密钥**：用于身份验证的私有 API 密钥。 |
| `BRid=GE_URL` | `aifront.py` | 您的“个人 Gemini”中转接口地址。 |
| `SSL Certs` | `midserver.py`, `aifront.py` | 确保证书和私钥文件（.pem 和 .key）位于脚本同级目录。 |

---

### 2. 部署步骤

#### **A. 本地 PC 端 (执行 Agent)**

1. **安装 OpenClaw**：OpenClaw 是您“个人 Gemini”的神经系统。访问 [OpenClaw.io](https://www.google.com/search?q=https://openclaw.io)。
2. **启动客户端**：安装依赖并运行 `client.py`。

```bash
pip install asyncio websockets
python client.py

```

#### **B. 公网服务器端 (中转枢纽)**

1. **启动中转引擎 `midserver.py**`：负责 WSS 隧道维护与 API 路由。

```bash
pip install fastapi uvicorn websockets pydantic
python midserver.py

```

2. **启动网页前端 `aifront.py**`：提供对话式交互 UI。

```bash
pip install flask requests
python aifront.py

```

---

### 🏗️ 系统架构

1. **PC (大脑)**：通过有状态的 WSS 反向隧道连接。
2. **中转服务器 (网关)**：将 Gemini 协议翻译为硬件底层动作。
3. **前端 (交互界面)**：为您的本地硬件提供对话式 UI 控制台。

---

### 🛡️ Security / 安全提醒

* **强制 HTTPS**：在公网环境下务必配合 SSL 证书使用 HTTPS。
* **凭据保护**：严禁泄露任何 Token 或 密钥。
* **有状态隐私**：请记住该 API 拥有系统访问权限，务必保证安全性。



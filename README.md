# 🤖 Gemini AI LINE Chatbot (Hearts-Echo)

這是一個基於 **FastAPI** 與 **gemini-3.1-flash-lite-preview** 模型的 LINE 聊天機器人。
支援多輪對話記憶，並透過 **Docker** 部署於 DigitalOcean。

## 🚀 快速開始

### 1. 環境需求  

* Python 3.11+
* Docker (選配，用於本地測試)
* LINE Developer 帳號 (Channel Secret & Token)
* Google AI Studio API Key (Gemini API)

### 2. 本地環境建置  

1. 複製專案：

```bash
git clone <你的儲存庫網址>
cd chatbot
```

---------------------------------------------
建立虛擬環境並安裝套件：

``` bash
python -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
pip install -r requirements.txt
```

設定環境變數：
在根目錄建立 .env 檔案，內容如下：

``` bash
LINE_CHANNEL_SECRET=YourSecret
LINE_CHANNEL_ACCESS_TOKEN=YourToken
GOOGLE_API_KEY=YourGeminiKey
```

使用 Docker 執行
建立映像檔：

``` bash
docker build -t linebot .
```

啟動容器:

``` bash
docker run -p 8000:8000 --env-file .env linebot
```

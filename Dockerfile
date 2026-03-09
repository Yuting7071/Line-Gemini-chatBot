# 1. 使用官方 Python 輕量版
FROM python:3.11-slim

# 2. 設定容器內的工作目錄
WORKDIR /app

# 3. 複製 requirements.txt 並安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 複製目前目錄下的所有程式碼到容器
COPY . .

# 5. 告知容器要開啟 8000 埠
EXPOSE 8000

# 6. 啟動指令 (假設檔名是 main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
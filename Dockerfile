# 🟢 使用官方輕量版 Python 3.10 作為基礎底圖
FROM python:3.10-slim

# 🎯 核心關鍵：安裝 Linux 系統底層影像庫 (新版 Debian 改用 libgl1)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 設定貨櫃內部的工作目錄
WORKDIR /app

# 複製依賴清單並先行安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製地端專案的所有檔案與 YOLO 模型權重進貨櫃
COPY . .

# 強制給予一鍵啟動腳本執行權限
RUN chmod +x run.sh

# 暴露前端 (8501) 與 後端 (8000) 的網路埠口
EXPOSE 8000
EXPOSE 8501

# 貨櫃啟動時的黃金總指揮指令
CMD ["./run.sh"]
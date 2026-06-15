#!/bin/bash

echo "☕ [Coffee Bean] 正在啟動業界級 AI 戰情室系統..."

# 1. 在背景悄悄啟動 FastAPI 後端大腦 (Port 8000)
echo "⚡ 1/2 正在點火 FastAPI 後端大腦..."
uvicorn main:app --host 127.0.0.1 --port 8000 > uvicorn.log 2>&1 &

# 稍微等待 2 秒，確保後端大腦跟 MySQL 連線完全清醒
sleep 2

# 2. 啟動 Streamlit 前端網頁 (Port 8501)
echo "🎨 2/2 正在啟動 Streamlit 精美前端..."
streamlit run frontend.py --server.port 8501

#./run.sh
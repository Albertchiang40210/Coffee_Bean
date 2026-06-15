import os
import io
import pymysql
import webbrowser
import threading
import time
from fastapi import FastAPI, File, UploadFile
from ultralytics import YOLO
from PIL import Image

app = FastAPI(title="☕ 咖啡豆影像辨識與資料庫系統 API")

# 資料庫連線設定
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "P@ssw0rd") 
DB_NAME = os.getenv("DB_NAME", "coffee_bean_db")

# 強制指定絕對路徑
MODEL_PATH = os.path.abspath('coffee_result/app.nano/weights/best.pt')
print(f"🔍 [AI 核心] 正在載入 YOLO 權重: {MODEL_PATH}")

if not os.path.exists(MODEL_PATH):
    print(f"🔴 [警告] 嚴重錯誤：找不到 {MODEL_PATH} 檔案！請確認路徑是否正確！")

model = YOLO(MODEL_PATH)

# 🟢 在網頁伺服器啟動時，自動執行「防呆建表」
@app.on_event("startup")
def init_db_and_ui():
    print(f"📦 [AI 核心標籤清單] 模型原始標籤為: {list(model.names.values())}")
    
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, autocommit=True)
        with conn.cursor() as cursor:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS coffee_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                detected_count INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_sql)
        conn.close()
        print("🟢 資料庫與 coffee_logs 表格已成功自動建立！")
    except Exception as e:
        print(f"🔴 自動建表失敗: {str(e)}")

@app.get("/")
def read_root():
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, autocommit=True)
        conn.close()
        return {"status": "success", "database": "Connected and Table is ready!"}
    except Exception as e:
        return {"status": "warning", "database": f"Error: {str(e)}"}

@app.post("/predict")
async def predict_coffee(file: UploadFile = File(...)):
    request_object_content = await file.read()
    image = Image.open(io.BytesIO(request_object_content)).convert("RGB")
    
    # 執行 YOLOv8 推理
    results = model(image)
    detected_classes = []
    
    for r in results:
        # 🎯 模式一：如果模型是「物件偵測模型」 (有邊框 boxes)
        if hasattr(r, 'boxes') and r.boxes is not None and r.boxes.cls is not None and len(r.boxes.cls) > 0:
            for c in r.boxes.cls:
                raw_name = model.names[int(c)]
                detected_classes.append(raw_name.capitalize())
        
        # 🎯 模式二：如果模型是「影像分類模型」 (有核心機率 probs) -> 修正你的盲區！
        elif hasattr(r, 'probs') and r.probs is not None:
            top1_idx = int(r.probs.top1)         # 拿到機率最高的類別編號
            top1_conf = float(r.probs.top1conf)  # 拿到該類別的信心度
            
            # 只要信心度大於 15%，就認定這張圖代表該種咖啡豆
            if top1_conf >= 0.15:
                raw_name = model.names[top1_idx]
                detected_classes.append(raw_name.capitalize())
            
    # 將辨識結果寫入資料庫
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, autocommit=True)
        with conn.cursor() as cursor:
            sql = "INSERT INTO coffee_logs (filename, detected_count) VALUES (%s, %s)"
            cursor.execute(sql, (file.filename, len(detected_classes)))
        conn.close()
        db_status = "Saved to Database Successfully!"
    except Exception as e:
        db_status = f"Failed to save to DB: {str(e)}"
            
    return {
        "status": "success",
        "filename": file.filename,
        "detected": detected_classes,
        "database_record": db_status,
        "message": f"成功辨識！偵測到 {len(detected_classes)} 個咖啡豆目標。"
    }
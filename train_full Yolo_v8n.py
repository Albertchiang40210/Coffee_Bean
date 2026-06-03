from ultralytics import YOLO

# 1. 載入模型 (yolov8n-cls 是專門做影像分類的輕量模型)
model = YOLO('yolov8n-cls.pt') 

# 2. 啟動訓練
# model = YOLO('yolov8l-cls.pt') # 降一階，選 Large

results = model.train(
    data='/Users/albert/Documents/Coffee_Project/coffee_dataset',
    epochs=100,
    imgsz=416,             # 稍微降低一點點解析度，減輕 GPU 壓力
    batch=16,              # 讓記憶體和核心有喘息空間
    name='coffee_m5_safe_large', 
    device='mps'           
)
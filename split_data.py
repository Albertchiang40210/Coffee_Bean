import os
import random
import shutil

# 1. 設定路徑
base_path = "/Users/albert/Documents/Coffee_Project/coffee_dataset"
train_path = os.path.join(base_path, "train")
val_path = os.path.join(base_path, "val")

# 2. 如果沒有 val 資料夾就建立它
if not os.path.exists(val_path):
    os.makedirs(val_path)

# 3. 遍歷 train 裡的每個類別資料夾
classes = [d for d in os.listdir(train_path) if not d.startswith('.')]

for cls in classes:
    src_folder = os.path.join(train_path, cls)
    dst_folder = os.path.join(val_path, cls)
    
    # 建立 val 下的子資料夾
    os.makedirs(dst_folder, exist_ok=True)
    
    # 取得該類別所有照片
    images = [f for f in os.listdir(src_folder) if not f.startswith('.')]
    
    # 計算 20% 是多少張
    val_count = int(len(images) * 0.2)
    print(f"📦 類別 [{cls}]: 總共 {len(images)} 張，將隨機搬移 {val_count} 張到驗證集...")
    
    # 隨機挑選並搬移
    val_images = random.sample(images, val_count)
    for img in val_images:
        shutil.move(os.path.join(src_folder, img), os.path.join(dst_folder, img))

print("\n✅ 數據隨機拆分完成！你現在可以啟動訓練了。")
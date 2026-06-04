# ☕ AI Coffee Bean Quality QC & Desktop Classification System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-green)](https://github.com/ultralytics/ultralytics)
[![GUI](https://img.shields.io/badge/UI-CustomTkinter-orange)](https://github.com/TomSchimansky/CustomTkinter)

這是一個專為精品咖啡產業設計的 **AI 咖啡生豆質量檢測與烘焙度品管桌面應用程式**。系統基於 YOLOv8 進行客製化物件偵測訓練，並使用 CustomTkinter 打造現代化、跨平台的桌面操作介面，支援影像拖曳辨識（Drag and Drop），能即時挑出 10 種不同狀態的咖啡豆與雜質異物，協助烘焙師與品豆師提升品管效率。

---

## 🚀 核心技術亮點 (Key Features)

- **現代化 GUI 互動設計:** 採用 `CustomTkinter` 框架建構支援深色模式 (Dark Mode) 的專用軟體，並整合 `tkinterdnd2` 實現直覺的圖片拖曳即時推理體驗，大幅優化使用者操作流程。
- **異步多執行緒處理 (Multi-Threading):** 將 YOLOv8 推理核心部署於獨立的背景執行緒 (Background Thread)，完美防範 AI 模型在大圖推理時造成 GUI 主介面凍結與卡頓，確保流暢的使用者體驗。
- **商業化數據映射 (Data Mapping):** 建立全中文化字典結構（`COFFEE_DATA`）進行預測類別轉換，輸出自定義色彩編碼 (Hex Color)、Emoji 與警報標籤，方便現場品管人員第一時間抓出高風險瑕疵豆。

---

## 📐 系統架構與執行緒設計 (System & Threading Architecture)
[ 使用者操作 GUI 介面 ] ──( 拖曳/選取圖片 )──> [ 主執行緒 Main Thread ]
│ (不阻塞 UI)
▼ 建立背景執行緒
[ 背景執行緒 Background Thread ]
│
▼ 執行 AI 推理
[ YOLOv8 模型辨識 (best.pt) ]
│
▼ 映射中文與色彩
[ 類別數據轉換 (COFFEE_DATA) ]
│
▼ 安全返回更新
[ 畫面即時呈現辨識結果 ] <────────────────────────────┘

---

## 📂 專案目錄結構 (Project Structure)

COFFEE_BEAN/
├── .venv                 # Python 虛擬環境
├── coffee_dataset/       # 包含 10 類別的咖啡豆訓練與驗證影像集
├── coffee_result/        # 儲存訓練出的權重檔 (包含 app.nano/weights/best.pt)
├── COFFEE驗證素材/        # 用於 Demo 與測試的生豆/烘焙豆實際影像
├── app_nano.py           # 系統主程式 (CustomTkinter GUI 介面與多執行緒 AI 邏輯)
├── split_data.py         # 自動化資料集劃分腳本 (Train / Val / Test)
└── train_full_Yolo_v8n.py# YOLOv8 完整訓練與超參數配置腳本

🔍 支援辨識之 10 大類別 (Classification Classes)
本系統能精準識別並歸類以下咖啡豆狀態與缺陷：
•	生豆瑕疵與異物: Defective (❌ 瑕疵損害豆) | Non_Coffee (⚠️ 非咖啡異物/如石頭、支梗)
•	精品與特殊品相: Healthy (✅ 優質健康豆) | Peaberry (🥜 優質圓豆) | Longberry (🥖 優質長豆) | Premium (💎 特級精品豆)
•	烘焙狀態分類: Green (🌿 未烘焙生豆) | Light (☀️ 淺焙咖啡豆) | Medium (☕ 中焙咖啡豆) | Dark (🔥 深焙咖啡豆)
🛠️ 快速開始 (Getting Started)
1. 環境安裝
請確保環境已安裝 Python 3.10+，並執行以下指令安裝依賴套件（包含 GUI 與拖曳套件）：
pip install ultralytics pillow customtkinter tkinterdnd2

2. 啟動桌面軟體
進入專案目錄後，直接執行主程式即可開啟現代化 AI 視窗：
python app_nano.py

開啟後，可以直接將 COFFEE驗證素材/ 資料夾中的圖片拖曳進視窗中進行測試！
📈 未來優化方向 (Future Roadmap)
	1.	結合工業相機 (SDK 串接): 導入 Basler 或大恆工業相機，透過 OpenCV 連續採樣產線輸送帶，將軟體升級為產線即時自動化 AOI 光學檢測系統。
	2.	軟體獨立封裝 (Executable): 使用 PyInstaller 將本專案封裝為獨立的 .exe (Windows) 或 .app (macOS) 執行檔，實現無 Python 環境下的單機快速部署。

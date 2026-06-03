import os
import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import customtkinter as ctk
from PIL import Image, ImageTk
import time
import threading

# YOLO 套件檢查
try:
    from ultralytics import YOLO
except ImportError:
    print("找不到 ultralytics，請執行 pip install ultralytics")
    exit(1)

# ==========================================
# 🛑 模型路徑配置 (請確保路徑正確) 🛑
# ==========================================
MODEL_PATH = 'coffee_result/app.nano/weights/best.pt'

# 商業配色
UI_THEME = {
    "bg": "#121212", 
    "card_bg": "#1E1E1E", 
    "primary": "#3498db",
    "sub_text": "#AAAAAA"
}

# 全中文化類別映射
COFFEE_DATA = {
    "Defective": {"name": "❌ 瑕疵損害豆", "color": "#ff4d4d", "desc": "品質異常：包含蟲蛀、發霉或破損"},
    "Healthy":   {"name": "✅ 優質健康豆", "color": "#2ecc71", "desc": "品質優良：外觀完整且色澤均勻"},
    "peaberry":  {"name": "🥜 優質圓豆 (Peaberry)", "color": "#3498db", "desc": "特殊品相：風味濃郁的單一種子圓豆"},
    "longberry": {"name": "🥖 優質長豆 (Longberry)", "color": "#9b59b6", "desc": "特色品相：外型修長，具備特殊風味潛力"},
    "premium":   {"name": "💎 特級精品豆 (Premium)", "color": "#f1c40f", "desc": "頂級品質：顆粒飽滿，具備極高商業價值"},
    "Dark":      {"name": "🔥 深焙咖啡豆", "color": "#8d6e63", "desc": "烘焙程度：深焙 (Dark Roast)"},
    "Green":     {"name": "🌿 未烘焙生豆", "color": "#aed581", "desc": "原始狀態：乾燥咖啡生豆"},
    "Medium":    {"name": "☕ 中焙咖啡豆", "color": "#d7ccc8", "desc": "烘焙程度：中焙 (Medium Roast)"},
    "Light":     {"name": "🔆 淺焙咖啡豆", "color": "#ffecb3", "desc": "烘焙程度：淺焙 (Light Roast)"},
    "Non_Coffee":{"name": "⚠️ 雜質異物", "color": "#f1c40f", "desc": "非咖啡豆物體，建議立即移除"}
}

class CoffeeInsightPro(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.title("Coffee Insight Pro - 智能鑑定系統")
        self.geometry("1150x750") # 稍微增加總寬度以配合側邊欄
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=UI_THEME["bg"])

        self.model = None
        self.tk_image = None
        
        self.setup_ui()
        # 異步載入模型
        threading.Thread(target=self.load_yolo, daemon=True).start()

    def setup_ui(self):
        # --- 1. 專業側邊欄 (已優化寬度) ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color=UI_THEME["card_bg"])
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False) # 強制維持寬度
        
        # 優化後的 Logo：增加左右留白 padx=30
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="☕ Coffee Bean AI", 
            font=("Arial", 26, "bold"), 
            text_color=UI_THEME["primary"]
        )
        self.logo_label.pack(pady=(60, 40), padx=30, anchor="w")
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="系統狀態: 初始化...", font=("Arial", 14), text_color="gray")
        self.status_label.pack(side="bottom", pady=40)

        # --- 2. 主顯示區塊 ---
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        # 影像拖曳/導入區域
        self.drop_frame = ctk.CTkFrame(self.main_view, border_width=2, border_color="#333333", corner_radius=20, cursor="hand2")
        self.drop_frame.pack(fill="both", expand=True, pady=(0, 25))
        
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        self.img_display = ctk.CTkLabel(self.drop_frame, text="請將咖啡豆照片【拖曳】至此\n或 點擊區域選取樣本", font=("Arial", 18), text_color=UI_THEME["sub_text"])
        self.img_display.pack(expand=True)
        self.img_display.bind("<Button-1>", lambda e: self.on_manual_import())

        # --- 3. 結果顯示卡片 ---
        self.res_card = ctk.CTkFrame(self.main_view, height=200, corner_radius=20, fg_color=UI_THEME["card_bg"])
        self.res_card.pack(fill="x")
        self.res_card.pack_propagate(False)

        self.result_text = ctk.CTkLabel(self.res_card, text="READY", font=("Arial", 32, "bold"), text_color=UI_THEME["sub_text"])
        self.result_text.pack(expand=True, pady=(15, 0))
        
        self.desc_text = ctk.CTkLabel(self.res_card, text="等待樣本導入...", font=("Arial", 16), text_color="#666666")
        self.desc_text.pack(expand=True, pady=(0, 15))

    def load_yolo(self):
        try:
            self.model = YOLO(MODEL_PATH)
            self.after(0, lambda: self.status_label.configure(text="系統狀態: 就緒", text_color="#2ecc71"))
        except:
            self.after(0, lambda: self.status_label.configure(text="模型載入錯誤", text_color="red"))

    def handle_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isfile(path):
            self.process_sample(path)

    def on_manual_import(self):
        path = filedialog.askopenfilename(filetypes=[("影像檔案", "*.jpg *.png *.jpeg")])
        if path: self.process_sample(path)

    def process_sample(self, path):
        try:
            img = Image.open(path)
            # 根據主視窗動態縮放影像
            img.thumbnail((700, 500))
            self.tk_image = ImageTk.PhotoImage(img)
            self.img_display.configure(image=self.tk_image, text="")
            self.result_text.configure(text="🔍 AI 鑑定中...", text_color="white")
            threading.Thread(target=self.run_inference, args=(path,), daemon=True).start()
        except Exception as e:
            print(f"處理出錯: {e}")

    def run_inference(self, path):
        if not self.model: return
        start = time.time()
        results = self.model(path, verbose=False)
        probs = results[0].probs
        label = results[0].names[probs.top1]
        conf = probs.top1conf.item()
        ms = (time.time() - start) * 1000
        self.after(0, self.update_ui, label, conf, ms)

    def update_ui(self, label, conf, ms):
        # 匹配中文映射
        info = COFFEE_DATA.get(label, {"name": label, "color": "white", "desc": "未知類別"})
        
        # 1. 大標題與顏色
        self.result_text.configure(text=f"{info['name']}", text_color=info["color"])
        
        # 2. 優化描述區排版：將描述與信心度分開，看起來更清晰
        formatted_desc = f"{info['desc']}\n信心度: {conf*100:.1f}%  |  耗時: {ms:.1f}ms"
        self.desc_text.configure(text=formatted_desc, text_color=UI_THEME["sub_text"])
        
        # 3. 側邊欄狀態同步更新為白色，避免過多雜色，保持專業
        self.status_label.configure(text=f"最後鑑定: {info['name']}", text_color=UI_THEME["sub_text"])

if __name__ == "__main__":
    app = CoffeeInsightPro()
    app.mainloop()
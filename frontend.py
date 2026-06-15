import streamlit as st
import requests
from PIL import Image
import io
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="☕ 咖啡豆智能影像辨識系統",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 前端精美元件配色與敘事字典
COFFEE_DATA = {
    "Defective": {"name": "❌ 瑕疵損害豆", "color": "#ff4d4d", "desc": "品質異常：包含蟲蛀、發黴或破損"},
    "Healthy": {"name": "✅ 優質健康豆", "color": "#2ecc71", "desc": "品質優良：外觀完整且色澤均勻"},
    "Peaberry": {"name": "🥜 優質圓豆 (Peaberry)", "color": "#3498db", "desc": "特殊品相：風味濃郁的單一種子圓豆"},
    "Longberry": {"name": "🥖 優質長豆 (Longberry)", "color": "#9b59b6", "desc": "特色品相：外型修長，具備特殊風味潛力"},
    "Premium": {"name": "💎 特級精品豆 (Premium)", "color": "#f1c40f", "desc": "頂級品質：顆粒飽滿，具備極高商業價值"},
    "Dark": {"name": "🔥 深焙咖啡豆", "color": "#8d6e63", "desc": "烘焙程度：深焙 (Dark Roast)"},
    "Green": {"name": "🌿 未烘焙生豆", "color": "#aed581", "desc": "原始狀態：乾燥咖啡生豆"},
    "Medium": {"name": "☕ 中焙咖啡豆", "color": "#d7ccc8", "desc": "烘焙程度：中焙 (Medium Roast)"},
    "Light": {"name": "☀️ 淺焙咖啡豆", "color": "#ffecb3", "desc": "烘焙程度：淺焙 (Light Roast)"},
    "Non_Coffee": {"name": "⚠️ 雜質異物", "color": "#e67e22", "desc": "非咖啡物體，建議立即移除"}
}

# 頂部戰情室橫幅
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e130c 0%, #9a8478 100%); padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <h1 style="color: white; margin: 0; font-family: 'Helvetica Neue', sans-serif;">☕ COFFEE BEAN AI DASHBOARD</h1>
        <p style="color: #e0e0e0; margin: 5px 0 0 0; font-size: 16px;">工業級咖啡豆邊緣影像辨識系統 | YOLOv8 Core Engine</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([4, 6], gap="large")

# 左側：影像上傳區
with col_left:
    st.subheader("📥 影像來源輸入")
    uploaded_file = st.file_uploader("將咖啡豆照片拖曳至此處...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 待辨識原始影像", use_container_width=True)
        btn_trigger = st.button("🚀 執行 Edge AI 智能辨識", type="primary", use_container_width=True)
    else:
        st.info("💡 請先上傳一張咖啡豆照片以啟用 AI 辨識分析。")
        btn_trigger = False

# 右側：即時 analysis 戰情室
with col_right:
    st.subheader("📊 即時分析與資料庫紀錄")
    
    if uploaded_file is not None and btn_trigger:
        with st.spinner("⚡ 正在調用 YOLOv8 模型進行神經網路推理..."):
            try:
                # 打包檔案並精準對接本地端 8000 後端大腦
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post("http://127.0.0.1:8000/predict", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    detected_list = result.get("detected", [])
                    db_record_status = result.get("database_record", "No status received")
                    
                    # 1. 頂部三大核心指標數據卡
                    m1, m2, m3 = st.columns(3)
                    m1.metric("總偵測數量", f"{len(detected_list)} 顆")
                    
                    counts = {}
                    for item in detected_list:
                        counts[item] = counts.get(item, 0) + 1
                    
                    # 🎯 核心導正：將所有的品相與烘焙程度完整納入良品池計數
                    healthy_count = (
                        counts.get("Healthy", 0) + 
                        counts.get("Premium", 0) + 
                        counts.get("Longberry", 0) + 
                        counts.get("Peaberry", 0) +
                        counts.get("Light", 0) + 
                        counts.get("Medium", 0) + 
                        counts.get("Dark", 0) + 
                        counts.get("Green", 0)
                    )
                    defect_count = counts.get("Defective", 0) + counts.get("Non_Coffee", 0)
                    
                    m2.metric("良品總數", f"{healthy_count} 顆", delta=f"+{healthy_count}" if healthy_count > 0 else None)
                    m3.metric("瑕疵異物", f"{defect_count} 顆", delta=f"-{defect_count}" if defect_count > 0 else None, delta_color="inverse")
                    
                    # 資料庫即時同步狀態看板
                    st.markdown("### 🗄️ SQL 資料庫同步日誌")
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if "Successfully" in db_record_status:
                        st.success(f"""
                            **🟢 成功同步至本地端 MySQL 資料庫！**  
                            * **寫入時間**：`{current_time}`  
                            * **資料表名**：`coffee_logs`  
                            * **紀錄內容**：檔案 `{uploaded_file.name}` 辨識出 `{len(detected_list)}` 個目標已成功寫入。
                        """)
                    else:
                        st.error(f"🔴 資料庫寫入失敗！原因：{db_record_status}")
                    
                    st.markdown("---")
                    
                    # 2. 下方圖表與明細卡片呈現
                    if detected_list:
                        sub_left, sub_right = st.columns([4, 6])
                        with sub_left:
                            st.write("📈 **類別分佈圖**")
                            df_chart = pd.DataFrame([
                                {"類別": COFFEE_DATA.get(k, {"name": k})["name"], "數量": v} 
                                for k, v in counts.items()
                            ])
                            st.bar_chart(df_chart.set_index("類別"), y="數量", color="#9a8478")
                        
                        with sub_right:
                            st.write("📋 **詳細明細清單**")
                            for class_name, count in counts.items():
                                info = COFFEE_DATA.get(class_name, {"name": class_name, "color": "#aaaaaa", "desc": "常規咖啡豆項目"})
                                
                                st.markdown(
                                    f"""
                                    <div style="padding:12px; border-radius:8px; background-color:#262730; border-left:6px solid {info['color']}; margin-bottom:8px;">
                                        <div style="display:flex; justify-content:content; align-items:center;">
                                            <span style="font-weight:bold; color:white; font-size:16px;">{info['name']}</span>
                                            <span style="background-color:{info['color']}; color:black; padding:2px 10px; border-radius:12px; font-weight:bold; font-size:14px; margin-left:auto;">{count} 顆</span>
                                        </div>
                                        <div style="font-size:12px; color:#AEC6CF; margin-top:4px;">{info['desc']}</div>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                    else:
                        st.warning("⚠️ 未偵測到明確的咖啡豆標籤。")
                else:
                    st.error(f"🔴 後端伺服器回應異常，狀態碼: {response.status_code}")
            except Exception as e:
                st.error(f"🔴 後端連線或網頁渲染失敗。詳細錯誤訊息: {str(e)}")
    else:
        st.markdown("""
            <div style="text-align: center; padding: 50px; color: #888888; border: 2px dashed #444444; border-radius: 10px;">
                <span style="font-size: 48px;">📊</span>
                <p style="margin-top: 15px; font-size: 16px;">等待 AI 推理結果生成...</p>
                <p style="font-size: 12px; color: #666666;">執行辨識後，此處將即時展示良率統計、圖表分析與資料庫同步狀態。</p>
            </div>
        """, unsafe_allow_html=True)
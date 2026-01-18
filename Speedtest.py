import streamlit as st
import pandas as pd
import datetime
import speedtest
import requests
import os
from groq import Groq

# Cấu hình file lưu trữ và trang
CSV_FILE = "network_history.csv"
st.set_page_config(page_title="Network AI Diagnostic", layout="wide", page_icon="🌐")

# ================== 1. CUSTOM STYLE (CSS) ==================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .title-container { text-align: center; padding: 1.5rem 0; }
    .title { font-size: 45px; font-weight: 800; color: #1e3a8a; margin-bottom: 0px; letter-spacing: -1px; }
    .subtitle { font-size: 16px; color: #64748b; margin-bottom: 20px; }
    .ai-box { background: #ffffff; border-radius: 15px; padding: 20px; border-left: 8px solid #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 20px; line-height: 1.6; color: #1e293b; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; font-weight: 600; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    </style>
""", unsafe_allow_html=True)

# ================== 2. HÀM TIỆN ÍCH (LOGIC) ==================

def save_result(download, upload, ping, loc, country):
    """Lưu kết quả vào CSV và trả về DataFrame"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_new = pd.DataFrame([[now, download, upload, ping, loc, country]],
                          columns=["time","download","upload","ping","location","country"])
    if os.path.exists(CSV_FILE):
        df_old = pd.read_csv(CSV_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(CSV_FILE, index=False)
    return df

def measure_network():
    """Đo tốc độ mạng với trạng thái hiển thị chi tiết"""
    # Khởi tạo spinner tổng quát
    with st.spinner("🚀 Đang khởi tạo hệ thống đo..."):
        try:
            stt = speedtest.Speedtest()
            status_text = st.empty() # Vùng hiển thị text trạng thái thay đổi liên tục
            
            status_text.info("📡 Đang tìm kiếm máy chủ có phản hồi nhanh nhất...")
            stt.get_best_server()
            
            status_text.info("⬇️ Đang kiểm tra tốc độ Download (Vui lòng chờ)...")
            download = round(stt.download() / 1e6, 2)
            
            status_text.info("⬆️ Đang kiểm tra tốc độ Upload (Vui lòng chờ)...")
            upload = round(stt.upload() / 1e6, 2)
            
            status_text.info("📡 Đang tính toán độ trễ (Ping)...")
            ping = round(stt.results.ping, 2)
            
            status_text.empty() # Xóa trạng thái sau khi hoàn tất
            
            # Lấy thông tin IP/Vị trí
            try:
                loc_json = requests.get("https://ipinfo.io/json", timeout=5).json()
                loc = loc_json.get("city", "Unknown")
                country = loc_json.get("country", "Unknown")
            except:
                loc, country = "Unknown", "Unknown"
                
            return download, upload, ping, loc, country
        except Exception as e:
            st.error(f"❌ Không thể đo tốc độ: {e}")
            return None, None, None, None, None

# ================== 3. GIAO DIỆN CHÍNH ==================

# Header
st.markdown("""
    <div class="title-container">
        <div class="title">🌐 Network AI Diagnostic</div>
        <div class="subtitle">Phân tích & Chẩn đoán băng thông thời gian thực với Trí tuệ nhân tạo</div>
        <p style="color: #64748b;">Sản phẩm của <a href="https://nguyenducngoc.vn/" target="_blank" style="color: #3b82f6; font-weight: 600; text-decoration: none;">Nguyễn Đức Ngọc</a></p>
    </div>
""", unsafe_allow_html=True)

# Layout Sidebar và Nội dung
sidebar, content = st.columns([1, 3], gap="large")

with sidebar:
    st.markdown("### 🎮 Trung tâm điều khiển")
    btn_run = st.button("🚀 BẮT ĐẦU ĐO TỐC ĐỘ")
    btn_history = st.button("📜 XEM LỊCH SỬ HỆ THỐNG")
    st.divider()
    st.info("💡 **Gợi ý:** Để kết quả chính xác, hãy tạm dừng các hoạt động livestream hoặc tải file nặng.")

with content:
    if btn_run:
        # Thực hiện đo
        d, u, p, l, c = measure_network()
        
        if d is not None:
            # Lưu dữ liệu
            df = save_result(d, u, p, l, c)
            st.toast("✅ Đã hoàn thành đo tốc độ!", icon="🎉")

            # Hiển thị Metrics (Chỉ số)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("⬇️ Download", f"{d} Mbps")
            m2.metric("⬆️ Upload", f"{u} Mbps")
            m3.metric("📡 Ping", f"{p} ms")
            m4.metric("📍 Khu vực", f"{l}, {c}")

            # Tabs hiển thị chi tiết
            tab1, tab2 = st.tabs(["📊 Biểu đồ phân tích", "🤖 Tư vấn từ Chuyên gia AI"])
            
            with tab1:
                st.subheader("Xu hướng 10 lần đo gần nhất")
                st.line_chart(df.tail(10).set_index("time")[["download","upload","ping"]])
            
            with tab2:
                if st.secrets.get("GROQ_API_KEY"):
                    with st.spinner("🤖 Chuyên gia AI đang phân tích dữ liệu..."):
                        try:
                            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                            prompt = f"Kết quả mạng: Download {d}Mbps, Upload {u}Mbps, Ping {p}ms tại {l}, {c}. Hãy đóng vai chuyên gia IT đánh giá chi tiết và đưa ra lời khuyên tối ưu (dưới 100 từ)."
                            res = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role":"user","content":prompt}]
                            )
                            ai_text = res.choices[0].message.content
                            st.markdown(f'<div class="ai-box"><b>💡 Phân tích kỹ thuật:</b><br><br>{ai_text}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Lỗi AI: {e}")
                else:
                    st.warning("⚠️ Chưa cấu hình GROQ_API_KEY trong Secrets.")

    elif btn_history:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            st.markdown("### 📂 Lịch sử đo tốc độ")
            st.dataframe(df.sort_values(by="time", ascending=False), use_container_width=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.download_button("📥 Tải file dữ liệu CSV", df.to_csv(index=False), "network_history.csv")
            with c2:
                if st.button("🗑️ Xóa toàn bộ lịch sử"):
                    os.remove(CSV_FILE)
                    st.success("Đã xóa dữ liệu. Đang tải lại...")
                    st.rerun()
        else:
            st.warning("Chưa có dữ liệu lịch sử nào được ghi lại.")
    
    else:
        # Màn hình chờ
        st.write("---")
        st.markdown("""
            <div style="text-align: center; color: #64748b; padding-top: 50px;">
                <h3>Sẵn sàng kiểm tra mạng?</h3>
                <p>Nhấn nút <b>Bắt đầu đo tốc độ</b> ở bên trái để khởi động quy trình chẩn đoán.</p>
            </div>
        """, unsafe_allow_html=True)

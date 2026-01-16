import streamlit as st
import speedtest
import time
import pandas as pd

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Internet Speed Test Pro", page_icon="⚡")

st.title("⚡ Kiểm tra tốc độ mạng")
st.markdown("Hệ thống đang mô phỏng luồng dữ liệu để bạn dễ quan sát.")

if st.button("🚀 Bắt đầu đo ngay!"):
    try:
        # Khởi tạo speedtest
        s = speedtest.Speedtest()
        
        with st.status("🛠️ Đang chuẩn bị hệ thống...", expanded=True) as status:
            st.write("🔍 Đang tìm kiếm máy chủ tối ưu nhất...")
            s.get_best_server()
            time.sleep(1) # Tạo độ trễ nhỏ để người dùng kịp nhìn
            
            # --- ĐO DOWNLOAD ---
            status.update(label="📥 Đang đo tốc độ Download...", state="running")
            download_progress = st.progress(0)
            chart_data = []
            chart_placeholder = st.empty()
            
            # Giả lập hiệu ứng biểu đồ đang chạy (vì thư viện đo xong mới trả kết quả một lần)
            for i in range(1, 101, 10):
                download_progress.progress(i)
                chart_data.append(i * 2) # Tạo dữ liệu giả lập cho biểu đồ
                chart_placeholder.area_chart(chart_data, height=150)
                time.sleep(0.1)
            
            download_speed = s.download() / 1_000_000
            download_progress.progress(100)
            st.write(f"✅ Hoàn thành Download: **{download_speed:.2f} Mbps**")

            # --- ĐO UPLOAD ---
            status.update(label="📤 Đang đo tốc độ Upload...", state="running")
            upload_progress = st.progress(0)
            for i in range(1, 101, 10):
                upload_progress.progress(i)
                time.sleep(0.1)
                
            upload_speed = s.upload() / 1_000_000
            upload_progress.progress(100)
            st.write(f"✅ Hoàn thành Upload: **{upload_speed:.2f} Mbps**")
            
            ping = s.results.ping
            status.update(label="📊 Tổng hợp kết quả!", state="complete")

        # --- HIỂN THỊ KẾT QUẢ ĐẸP MẮT ---
        st.divider()
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("### ⬇️ Download")
            st.subheader(f"{download_speed:.2f}")
            st.caption("Mbps")
            
        with c2:
            st.markdown("### ⬆️ Upload")
            st.subheader(f"{upload_speed:.2f}")
            st.caption("Mbps")
            
        with c3:
            st.markdown("### 🕒 Ping")
            st.subheader(f"{ping:.0f}")
            st.caption("ms")

        # Hiển thị biểu đồ so sánh cuối cùng
        results_df = pd.DataFrame({
            "Dịch vụ": ["Download", "Upload"],
            "Mbps": [download_speed, upload_speed]
        })
        st.bar_chart(data=results_df, x="Dịch vụ", y="Mbps", color="#FF4B4B")

    except Exception as e:
        st.error(f"⚠️ Lỗi kết nối: {e}")
        st.info("Gợi ý: Nếu chạy trên Cloud, server có thể chặn kết nối speedtest. Hãy thử chạy lại hoặc chạy trực tiếp trên máy tính (Local).")

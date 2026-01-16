import streamlit as st
import speedtest # Thư viện này được cài từ gói speedtest-cli

st.set_page_config(page_title="Internet Speed Test", page_icon="🌐")

st.title("🌐 Kiểm tra tốc độ mạng")

# Kiểm tra xem thư viện có hoạt động không
if st.button("Bắt đầu đo ngay!"):
    try:
        with st.status("Đang thực hiện đo tốc độ...", expanded=True) as status:
            st.write("Đang tìm máy chủ tốt nhất...")
            s = speedtest.Speedtest()
            s.get_best_server()
            
            st.write("Đang đo Download...")
            download_speed = s.download() / 1_000_000
            
            st.write("Đang đo Upload...")
            upload_speed = s.upload() / 1_000_000
            
            ping = s.results.ping
            status.update(label="Đo hoàn tất!", state="complete")

        col1, col2, col3 = st.columns(3)
        col1.metric("Download", f"{download_speed:.2f} Mbps")
        col2.metric("Upload", f"{upload_speed:.2f} Mbps")
        col3.metric("Ping", f"{ping} ms")
        
    except Exception as e:
        st.error(f"Lỗi: {e}")
        st.info("Lưu ý: Speedtest đôi khi bị chặn bởi tường lửa của server Cloud.")

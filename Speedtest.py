import streamlit as st
import speedtest
import time

st.set_page_config(page_title="Internet Speed Test", page_icon="🌐")

st.title("🌐 Kiểm tra tốc độ mạng")
st.markdown("Nhấn nút dưới đây để bắt đầu đo tốc độ Internet của bạn.")

if st.button("Bắt đầu đo ngay!"):
    with st.status("Đang kết nối tới máy chủ...", expanded=True) as status:
        st.write("Đang tìm máy chủ tốt nhất...")
        st = speedtest.Speedtest()
        st.get_best_server()
        
        status.update(label="Đang đo tốc độ Download...", state="running")
        download_speed = st.download() / 1_000_000  # Chuyển sang Mbps
        
        status.update(label="Đang đo tốc độ Upload...", state="running")
        upload_speed = st.upload() / 1_000_000    # Chuyển sang Mbps
        
        ping = st.results.ping
        status.update(label="Hoàn thành!", state="complete", expanded=False)

    # Hiển thị kết quả bằng cột
    col1, col2, col3 = st.columns(3)
    col1.metric("Download", f"{download_speed:.2f} Mbps", delta_color="normal")
    col2.metric("Upload", f"{upload_speed:.2f} Mbps", delta_color="normal")
    col3.metric("Ping", f"{ping} ms", delta_color="inverse")

    # Hiển thị thông báo đánh giá
    if download_speed > 50:
        st.success("Mạng của bạn rất mạnh! Có thể xem phim 4K mượt mà.")
    elif download_speed > 20:
        st.info("Mạng ổn định cho các nhu cầu làm việc và học tập.")
    else:
        st.warning("Tốc độ mạng hơi thấp, có thể gây lag khi họp online.")

else:
    st.info("Chưa có dữ liệu. Hãy nhấn nút để bắt đầu.")

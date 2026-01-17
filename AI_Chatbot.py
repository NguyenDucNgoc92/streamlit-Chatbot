import streamlit as st
import requests
import json
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="NDN AI Assistant", page_icon="🤖", layout="wide")

# --- CSS CUSTOM (AVATAR TRÒN & HIỆU ỨNG) ---
st.markdown("""
<style>
    /* Hiệu ứng Fade In */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage { animation: fadeIn 0.5s ease-out; }

    /* Tiêu đề Gradient */
    .main-title {
        font-size: 3rem; font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4158D0, #C850C0, #FFCC70);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.5rem;
    }

    /* Footer link */
    .footer-text {
        text-align: center; font-size: 0.9rem; color: #666; margin-bottom: 2rem;
    }
    .footer-text a { color: #666; text-decoration: none; font-weight: bold; }
    .footer-text a:hover { color: #C850C0; }

    /* Avatar hình tròn trong Sidebar */
    .sidebar-avatar {
        display: block; margin-left: auto; margin-right: auto;
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; border: 3px solid #C850C0;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. MODAL ĐIỀU KHOẢN ---
if "agreed" not in st.session_state:
    st.session_state.agreed = False

@st.dialog("⚠️ QUY ĐỊNH SỬ DỤNG AN TOÀN")
def show_terms():
    st.markdown("""
    Chào mừng bạn đến với mô phỏng AI. Vui lòng lưu ý:
    * **KHÔNG CHIA SẺ DỮ LIỆU CÁ NHÂN** (mật khẩu, số thẻ, thông tin riêng tư...).
    * Dùng cho mục đích **trải nghiệm mô phỏng, học tập**.
    * Không yêu cầu thanh toán dưới mọi hình thức.
    """)
    if st.button("Tôi đã hiểu và đồng ý", use_container_width=True, type="primary"):
        st.session_state.agreed = True
        st.rerun()

if not st.session_state.agreed:
    show_terms()
    st.stop()

# --- 2. QUẢN LÝ LỊCH SỬ CHAT (Cấu trúc giống Gemini) ---
# Dùng để lưu trữ nhiều phiên chat khác nhau
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Phiên chat 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Phiên chat 1"

# --- SIDEBAR (AVATAR & LỊCH SỬ) ---
with st.sidebar:
    # Avatar hình tròn (Thay URL ảnh của bạn vào đây)
    st.markdown(f'<img src="https://ui-avatars.com/api/?name=NDN&background=random&size=128" class="sidebar-avatar">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>NDN Control</h3>", unsafe_allow_html=True)
    
    if st.button("➕ Tạo hội thoại mới", use_container_width=True):
        new_id = f"Phiên chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_id] = []
        st.session_state.current_session = new_id
        st.rerun()
    
    st.divider()
    st.subheader("Lịch sử trò chuyện")
    # Hiển thị danh sách các session đã chat
    for session_name in st.session_state.chat_sessions.keys():
        if st.button(f"💬 {session_name}", key=session_name, use_container_width=True):
            st.session_state.current_session = session_name
            st.rerun()

# --- 3. GIAO DIỆN CHÍNH ---
st.markdown('<div class="main-title">NDN AI ASSISTANT</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-text"><a href="https://nguyenducngoc.vn/" target="_blank">Một sản phẩm của Nguyễn Đức Ngọc | 1- 2026</a></div>', unsafe_allow_html=True)

# Lấy tin nhắn của session hiện tại
current_messages = st.session_state.chat_sessions[st.session_state.current_session]

# Hiển thị lịch sử chat của session này
for i, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Nút sửa prompt cho user (tin nhắn cuối)
        if i == len(current_messages) - 2 and message["role"] == "user":
             st.caption("Chế độ: Đã gửi (Bạn có thể gửi câu hỏi mới để ghi đè)")

# --- 4. XỬ LÝ CHAT ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

if prompt := st.chat_input("Hỏi NDN AI điều gì đó..."):
    # Lưu vào session hiện tại
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": current_messages,
                    "stream": True 
                },
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode("utf-8")
                    if line_text.startswith("data: "):
                        data_str = line_text[6:]
                        if data_str == "[DONE]": break
                        data_json = json.loads(data_str)
                        delta = data_json["choices"][0]["delta"].get("content", "")
                        full_response += delta
                        placeholder.markdown(full_response + " █")
            
            placeholder.markdown(full_response)
            current_messages.append({"role": "assistant", "content": full_response})
            # Cập nhật lại kho lưu trữ tổng
            st.session_state.chat_sessions[st.session_state.current_session] = current_messages
            
        except Exception as e:
            st.error(f"Lỗi: {e}")

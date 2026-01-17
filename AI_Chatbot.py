import streamlit as st
import requests
import json
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="NDN AI Pro", page_icon="💎", layout="wide")

# --- CSS CUSTOM (HIỆU ỨNG ĐẸP) ---
st.markdown("""
<style>
    /* Hiệu ứng Fade In cho tin nhắn */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Tùy chỉnh tiêu đề link */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4158D0, #C850C0, #FFCC70);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Bo góc cho khung chat */
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. MODAL ĐIỀU KHOẢN ---
if "agreed" not in st.session_state:
    st.session_state.agreed = False

@st.dialog("⚠️ QUY ĐỊNH SỬ DỤNG AN TOÀN")
def show_terms():
    st.warning("Vui lòng đọc kỹ trước khi bắt đầu")
    st.markdown("""
    - **KHÔNG CHIA SẺ DỮ LIỆU CÁ NHÂN**: Không nhập mật khẩu, số thẻ tín dụng hoặc thông tin nhạy cảm.
    - **MỤC ĐÍCH**: Sử dụng cho trải nghiệm mô phỏng, học tập và nghiên cứu.
    - **THANH TOÁN**: Đây là phiên bản miễn phí, hoàn toàn **không yêu cầu thanh toán**.
    - **HỆ THỐNG**: Sử dụng công nghệ Groq Llama 3 API.
    """)
    if st.button("Tôi đồng ý và cam kết tuân thủ", use_container_width=True, type="primary"):
        st.session_state.agreed = True
        st.rerun()

if not st.session_state.agreed:
    show_terms()
    st.stop()

# --- 2. GIAO DIỆN CHÍNH ---
st.markdown('<div class="main-title"><a href="https://nguyenducngoc.vn/" target="_blank" style="text-decoration: none; color: inherit;">NDN</a> AI ASSISTANT</div>', unsafe_allow_html=True)

# Lấy key
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Khởi tạo session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR NÂNG CẤP ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Control Center")
    if st.button("🆕 Tạo hội thoại mới", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Phiên bản: Pro 2.0 (Llama 3.3)")
    st.info("Hệ thống tự động tối ưu hóa câu trả lời dựa trên ngữ cảnh.")

# --- 3. HIỂN THỊ TIN NHẮN VỚI HIỆU ỨNG ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Nút sửa prompt cho tin nhắn cuối cùng của User
        if i == len(st.session_state.messages) - 2 and message["role"] == "user":
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("✏️ Sửa", key=f"edit_{i}", help="Chỉnh sửa câu hỏi này"):
                    st.session_state.edit_input = message["content"]
                    # (Tính năng sửa sẽ được xử lý qua logic session)

# --- 4. XỬ LÝ CHAT ---
if prompt := st.chat_input("Nhập câu hỏi tại đây..."):
    # Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Hiển thị Assistant phản hồi
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            "stream": True 
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, stream=True
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
                        # Thêm icon con trỏ nhấp nháy
                        placeholder.markdown(full_response + " █")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"⚠️ Có lỗi xảy ra: {str(e)}")

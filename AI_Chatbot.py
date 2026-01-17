import streamlit as st
import requests
import json

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="NDN AI Pro", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- CSS CUSTOM (UI CHUẨN GEMINI & FIX LINK) ---
st.markdown("""
<style>
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    
    .main-title {
        font-size: 3.5rem; font-weight: 600;
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: 5vh;
        font-family: 'Google Sans', sans-serif;
    }
    
    /* Style cho link không bị đổi màu xanh */
    .footer-link {
        text-decoration: none;
        color: #666 !important;
        transition: 0.3s;
    }
    .footer-link:hover {
        color: #4285F4 !important;
    }

    .footer-text {
        text-align: center; font-size: 0.9rem; margin-bottom: 30px;
    }

    /* Thẻ gợi ý trắng */
    div[data-testid="stColumn"] button {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        height: 120px !important;
        color: #3c4043 !important;
    }

    /* Avatar Sidebar */
    .sidebar-avatar-container {
        display: flex; justify-content: center; margin-bottom: 20px;
    }
    .sidebar-avatar {
        width: 80px; height: 80px; border-radius: 50%;
        background: #4285F4; color: white;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; font-weight: bold; border: 2px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- QUẢN LÝ SESSION STATE ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Phiên chat 1": []}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Phiên chat 1"
if "agreed" not in st.session_state:
    st.session_state.agreed = False

# --- 2. MODAL ĐIỀU KHOẢN ---
@st.dialog("⚠️ QUY ĐỊNH SỬ DỤNG")
def show_terms():
    st.markdown("""
    Chào mừng bạn đến với NDN Chatbot. Vui lòng lưu ý:
    * **KHÔNG CHIA SẺ DỮ LIỆU CÁ NHÂN** (mật khẩu, số thẻ, thông tin riêng tư...).
    * Dùng cho mục đích **trải nghiệm mô phỏng, học tập**.
    * Không yêu cầu thanh toán dưới mọi hình thức.
    * Tuân thủ pháp luật Việt Nam về quyền dữ liệu người dùng Luật Bảo vệ dữ liệu cá nhân 2025 và Nghị định 13/2023/NĐ-CP
    * Hãy lịch sử văn minh khi sử dụng
    """)
    if st.button("Tôi đã hiểu và đồng ý", use_container_width=True, type="primary"):
        st.session_state.agreed = True
        st.rerun()

if not st.session_state.agreed:
    show_terms()
    st.stop()

# --- 3. SIDEBAR (CẬP NHẬT LINK) ---
with st.sidebar:
    st.markdown('<div class="sidebar-avatar-container"><div class="sidebar-avatar">NDN</div></div>', unsafe_allow_html=True)
    
    st.markdown(f"""<div style="text-align:center;">
        <h2 style="background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; margin-bottom:0;">NDN AI ASSISTANT</h2>
        <p style="font-size:0.8rem;">
            <a href="https://nguyenducngoc.vn/" target="_blank" class="footer-link">Một sản phẩm của Nguyễn Đức Ngọc | 1- 2026</a>
        </p>
    </div>""", unsafe_allow_html=True)
    
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        new_id = f"Phiên chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_id] = []
        st.session_state.current_session = new_id
        st.rerun()
    
    st.divider()
    for session_name in list(st.session_state.chat_sessions.keys()):
        is_active = (session_name == st.session_state.current_session)
        if st.button(f"💬 {session_name}", key=f"side_{session_name}", use_container_width=True, type="secondary" if not is_active else "primary"):
            st.session_state.current_session = session_name
            st.rerun()

# --- 4. GIAO DIỆN CHÍNH ---
current_messages = st.session_state.chat_sessions[st.session_state.current_session]

# Hàm hiển thị Header chung cho cả màn hình trống và màn hình chat
def display_common_header():
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px;">
        <p style="font-size:0.9rem;">
            <a href="https://nguyenducngoc.vn/" target="_blank" class="footer-link">Một sản phẩm của Nguyễn Đức Ngọc | 1- 2026</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

if not current_messages:
    st.markdown('<div class="main-title">Hi Ngọc,<br>Where should we start?</div>', unsafe_allow_html=True)
    display_common_header()
    
    suggestions = [
        {"icon": "🎨", "text": "Tạo hình ảnh về thành phố tương lai"},
        {"icon": "💡", "text": "Lên ý tưởng học lập trình Python"},
        {"icon": "✍️", "text": "Viết email xin việc chuyên nghiệp"},
        {"icon": "🚀", "text": "Tối ưu hóa hiệu suất làm việc"}
    ]
    
    cols = st.columns(4)
    for i, sug in enumerate(suggestions):
        with cols[i]:
            if st.button(f"{sug['icon']}\n\n{sug['text']}", key=f"sug_{i}"):
                current_messages.append({"role": "user", "content": sug['text']})
                st.rerun()
else:
    # Trong phiên chat cũng hiện dòng thông tin sản phẩm phía trên
    st.caption(f"🚀 Phiên làm việc: {st.session_state.current_session}")
    display_common_header()
    
    for msg in current_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. XỬ LÝ NHẬP LIỆU & API ---
if prompt := st.chat_input("Nhập câu hỏi tại đây..."):
    current_messages.append({"role": "user", "content": prompt})
    st.rerun()

# Logic phản hồi (Chỉ chạy khi tin nhắn cuối cùng là của User)
if current_messages and current_messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"},
                json={"model": "llama-3.3-70b-versatile", "messages": current_messages, "stream": True},
                stream=True,
                timeout=20
            )
            for line in res.iter_lines():
                if line:
                    line_text = line.decode("utf-8")
                    if line_text.startswith("data: "):
                        data_str = line_text[6:]
                        if data_str == "[DONE]": break
                        delta = json.loads(data_str)["choices"][0]["delta"].get("content", "")
                        full_res += delta
                        placeholder.markdown(full_res + " ▌")
            
            placeholder.markdown(full_res)
            current_messages.append({"role": "assistant", "content": full_res})
            st.session_state.chat_sessions[st.session_state.current_session] = current_messages
            st.rerun() # Rerun để hiện nút gợi ý mà không chạy lại API
        except Exception as e:
            st.error(f"⚠️ Lỗi kết nối: {str(e)}")

# --- 6. GỢI Ý SAU CÂU TRẢ LỜI (FOLLOW-UP) ---
# Chỉ hiện khi tin nhắn cuối cùng là của Assistant
if current_messages and current_messages[-1]["role"] == "assistant":
    st.write("") # Tạo khoảng cách
    st.caption("Gợi ý cho bạn:")
    f_cols = st.columns(3)
    follow_ups = ["Giải thích rõ hơn", "Cho ví dụ cụ thể", "Tóm tắt ý chính"]
    for i, f_text in enumerate(follow_ups):
        if f_cols[i].button(f"🔍 {f_text}", key=f"fup_{i}", use_container_width=True):
            current_messages.append({"role": "user", "content": f_text})
            st.rerun()


import streamlit as st
import requests
import json

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="NDN AI Pro", page_icon="🤖", layout="wide")

# --- CSS CUSTOM (UI/UX NÂNG CAO) ---
st.markdown("""
<style>
    /* Ẩn Header mặc định của Streamlit để giống App hơn */
    header {visibility: hidden;}
    
    /* Hiệu ứng Fade In */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .stChatMessage { animation: fadeIn 0.5s ease-out; }

    /* Tiêu đề & Footer */
    .main-title {
        font-size: 3.5rem; font-weight: 800;
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: 5vh;
    }
    .sidebar-title {
        font-size: 3.5rem; font-weight: 300;
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-top: 5vh;
    }
    .footer-text { text-align: center; margin-bottom: 2rem; }
    .footer-text a { color: #5f6368; text-decoration: none; font-weight: 500; }

    /* Thẻ gợi ý (Gemini Style) */
    .suggestion-card {
        background: #f0f4f9; border-radius: 16px; padding: 20px;
        cursor: pointer; transition: 0.3s; border: none; text-align: left;
        height: 100%; display: flex; align-items: flex-end;
    }
    .suggestion-card:hover { background: #e3e8ef; }

    /* Avatar Sidebar */
    .sidebar-avatar {
        display: block; margin: 0 auto 10px auto;
        width: 80px; height: 80px; border-radius: 50%;
        border: 2px solid #9B72CB;
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

# --- 1. MODAL ĐIỀU KHOẢN ---
@st.dialog("⚠️ QUY ĐỊNH SỬ DỤNG")
def show_terms():
    st.markdown("""
    Chào mừng bạn đến với mô phỏng AI. Vui lòng lưu ý:
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

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown(f'<img src="https://ui-avatars.com/api/?name=Ngọc&background=4285F4&color=fff" class="sidebar-avatar">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">NDN AI ASSISTANT</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-text"><a href="https://nguyenducngoc.vn/" target="_blank">Một sản phẩm của Nguyễn Đức Ngọc | 1- 2026</a></div>', unsafe_allow_html=True)
    
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        new_id = f"Phiên chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_id] = []
        st.session_state.current_session = new_id
        st.rerun()
    
    st.divider()
    for session_name in list(st.session_state.chat_sessions.keys()):
        if st.button(f"💬 {session_name}", key=session_name, use_container_width=True):
            st.session_state.current_session = session_name
            st.rerun()

# --- 3. GIAO DIỆN CHÍNH ---
current_messages = st.session_state.chat_sessions[st.session_state.current_session]

if not current_messages:
    # HIỂN THỊ KHI CHƯA CÓ TIN NHẮN (GIỐNG ẢNH BẠN GỬI)
    st.markdown('<div class="main-title">Hi Ngọc, <br>Where should we start?</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-text"><a href="https://nguyenducngoc.vn/" target="_blank">Một sản phẩm của Nguyễn Đức Ngọc | 1- 2026</a></div>', unsafe_allow_html=True)
    
    # Grid gợi ý
    cols = st.columns(4)
    suggestions = [
        {"icon": "🎨", "text": "Tạo hình ảnh về thành phố tương lai"},
        {"icon": "💡", "text": "Lên ý tưởng học lập trình Python"},
        {"icon": "✍️", "text": "Viết email xin việc chuyên nghiệp"},
        {"icon": "🚀", "text": "Tối ưu hóa hiệu suất làm việc"}
    ]
    
    for i, col in enumerate(cols):
        with col:
            if st.button(f"{suggestions[i]['icon']}\n\n{suggestions[i]['text']}", key=f"sug_{i}"):
                current_messages.append({"role": "user", "content": suggestions[i]['text']})
                st.rerun()
else:
    # HIỂN THỊ LỊCH SỬ CHAT
    st.markdown(f"### {st.session_state.current_session}")
    for i, msg in enumerate(current_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 4. XỬ LÝ NHẬP LIỆU & GỢI Ý TIẾP THEO ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

if prompt := st.chat_input("Nhập câu hỏi tại đây..."):
    current_messages.append({"role": "user", "content": prompt})
    st.rerun()

# Logic phản hồi của AI
if current_messages and current_messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama-3.3-70b-versatile", "messages": current_messages, "stream": True},
                stream=True
            )
            for line in res.iter_lines():
                if line:
                    line_text = line.decode("utf-8")
                    if "data: " in line_text and "[DONE]" not in line_text:
                        delta = json.loads(line_text[6:])["choices"][0]["delta"].get("content", "")
                        full_res += delta
                        placeholder.markdown(full_res + " ▌")
            
            placeholder.markdown(full_res)
            current_messages.append({"role": "assistant", "content": full_res})
            st.session_state.chat_sessions[st.session_state.current_session] = current_messages
            st.rerun()
        except:
            st.error("Lỗi kết nối API.")

# --- GỢI Ý SAU CÂU TRẢ LỜI ---
if current_messages and current_messages[-1]["role"] == "assistant":
    st.markdown("---")
    st.caption("Bạn có thể muốn hỏi thêm:")
    follow_cols = st.columns(3)
    follow_ups = ["Giải thích chi tiết hơn", "Cho tôi ví dụ cụ thể", "Tóm tắt lại ý chính"]
    for i, f_text in enumerate(follow_ups):
        if follow_cols[i].button(f"🔍 {f_text}", key=f"follow_{i}"):
            current_messages.append({"role": "user", "content": f_text})
            st.rerun()



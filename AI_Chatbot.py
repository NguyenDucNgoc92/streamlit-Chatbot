import streamlit as st
import requests
import json

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI Chatbot Pro", page_icon="🚀")
st.title("🚀 My AI Assistant")
st.markdown("Cung cấp bởi mô hình **Llama 3.3 (Groq)**")

# --- QUẢN LÝ API KEY (LẤY TRỰC TIẾP TỪ SECRETS) ---
# Kiểm tra xem Key có tồn tại trong Secrets không
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ Không tìm thấy 'GROQ_API_KEY' trong phần Secrets của App!")
    st.stop() # Dừng app nếu không có Key

# --- KHỞI TẠO LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị hội thoại cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ NHẬP LIỆU ---
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi API Groq bằng phương thức POST
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": st.session_state.messages,
            "stream": True 
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode("utf-8")
                    if line_text.startswith("data: "):
                        data_str = line_text[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data_json = json.loads(data_str)
                            delta = data_json["choices"][0]["delta"].get("content", "")
                            full_response += delta
                            placeholder.markdown(full_response + "▌")
                        except json.JSONDecodeError:
                            continue
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Đã xảy ra lỗi kết nối: {str(e)}")

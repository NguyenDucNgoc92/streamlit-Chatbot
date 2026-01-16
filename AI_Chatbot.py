import streamlit as st
import requests
import json

# --- CẤU HÌNH ---
st.set_page_config(page_title="AI Chatbot Pro", page_icon="🚀")
st.title("🚀 My AI Assistant")

# Lấy trực tiếp key từ secrets (Nếu chưa cấu hình ở Streamlit Cloud, app sẽ báo lỗi hệ thống)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# --- LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ CHAT ---
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": st.session_state.messages,
            "stream": True 
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode("utf-8")
                if line_text.startswith("data: "):
                    data_str = line_text[6:]
                    if data_str == "[DONE]":
                        break
                    
                    data_json = json.loads(data_str)
                    delta = data_json["choices"][0]["delta"].get("content", "")
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

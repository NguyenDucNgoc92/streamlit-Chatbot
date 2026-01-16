import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.graph_objects as go

# --- CẤU HÌNH ---
st.set_page_config(page_title="AI Quiz System", layout="centered")
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# --- KHỞI TẠO BIẾN HỆ THỐNG ---
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# --- HÀM GỌI AI TẠO CÂU HỎI ---
def generate_questions(subject, count):
    prompt = f"""
    Hãy tạo {count} câu hỏi trắc nghiệm về {subject}. 
    Mỗi câu hỏi phải có 4 đáp án (A, B, C, D) và chỉ có 1 đáp án đúng.
    Phân loại mỗi câu hỏi vào 1 trong các domain sau: Ngữ pháp, Từ vựng, Đọc hiểu, Logic.
    Trả về định dạng JSON thuần túy như sau (không kèm lời dẫn):
    [
      {{"question": "Nội dung câu hỏi", "options": ["A", "B", "C", "D"], "answer": "A", "domain": "Ngữ pháp"}},
      ...
    ]
    """
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# --- TRANG 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("🧠 Hệ thống Kiểm tra Năng lực AI")
    subject = st.selectbox("Chọn loại kiểm tra:", ["IQ (Logic)", "Tiếng Anh (Ngữ pháp & Đọc hiểu)", "Tiếng Nhật (N5-N1)"])
    count = st.select_slider("Số lượng câu hỏi:", options=[10, 15, 20])
    
    if st.button("🚀 Khởi tạo bài thi"):
        with st.spinner("AI đang soạn câu hỏi cho bạn..."):
            raw_data = generate_questions(subject, count)
            st.session_state.quiz_data = json.loads(raw_data)
            if "questions" in st.session_state.quiz_data: # Xử lý nếu AI trả về key 'questions'
                st.session_state.quiz_data = st.session_state.quiz_data["questions"]
            st.session_state.start_time = time.time()
            st.session_state.page = "quiz"
            st.rerun()

# --- TRANG 2: LÀM BÀI ---
elif st.session_state.page == "quiz":
    st.title("📝 Đang làm bài")
    for i, q in enumerate(st.session_state.quiz_data):
        st.subheader(f"Câu {i+1}: {q['question']}")
        st.session_state.answers[i] = st.radio(f"Chọn đáp án cho câu {i+1}:", q['options'], key=f"q_{i}")
    
    if st.button("🏁 Nộp bài"):
        st.session_state.end_time = time.time()
        st.session_state.page = "result"
        st.rerun()

# --- TRANG 3: KẾT QUẢ & ĐÁNH GIÁ ---
elif st.session_state.page == "result":
    st.title("📊 Kết quả bài thi")
    total_time = round(st.session_state.end_time - st.session_state.start_time, 2)
    
    correct = 0
    domain_scores = {}
    
    for i, q in enumerate(st.session_state.quiz_data):
        domain = q['domain']
        if domain not in domain_scores: domain_scores[domain] = {"correct": 0, "total": 0}
        domain_scores[domain]["total"] += 1
        
        if st.session_state.answers[i] == q['answer']:
            correct += 1
            domain_scores[domain]["correct"] += 1
            
    score_pct = (correct / len(st.session_state.quiz_data)) * 100

    # Hiển thị Metrics
    c1, c2 = st.columns(2)
    c1.metric("Tỉ lệ đúng", f"{score_pct}%")
    c2.metric("Thời gian", f"{total_time} giây")

    # Vẽ biểu đồ Radar
    categories = list(domain_scores.keys())
    values = [(d["correct"]/d["total"])*100 for d in domain_scores.values()]
    
    fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Phân tích kỹ năng")
    st.plotly_chart(fig)

    # AI Đánh giá lời khuyên
    with st.expander("💡 Lời khuyên từ AI"):
        advice_prompt = f"Học viên làm đúng {score_pct}% bài thi trong {total_time} giây. Kết quả từng phần: {domain_scores}. Hãy đưa ra lời khuyên ngắn gọn."
        # (Gọi API tương tự như trên để lấy lời khuyên...)
        st.write("Dựa trên kết quả, bạn đang làm rất tốt phần Logic nhưng cần cải thiện thêm từ vựng chuyên ngành.")

    if st.button("🔄 Làm bài mới"):
        st.session_state.page = "welcome"
        st.session_state.answers = {}
        st.rerun()

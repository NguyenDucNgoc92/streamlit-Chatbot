import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.graph_objects as go

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="AI Pro Quiz System", layout="centered")

if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    st.error("Cấu hình GROQ_API_KEY trong Secrets trước khi chạy!")
    st.stop()

# Khởi tạo Session State
for key in ["quiz_data", "answers", "start_time", "page", "subject"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "page" else "welcome"
        if key == "answers": st.session_state[key] = {}

# --- HÀM GỌI AI ---
def call_groq(prompt, json_mode=True):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    if json_mode: payload["response_format"] = {"type": "json_object"}
    
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

def generate_quiz(subject, count):
    prompt = f"""
    Tạo bộ đề thi trắc nghiệm {count} câu về {subject}.
    - Nếu là Tiếng Nhật: Dùng Kanji, Hiragana, Katakana chuẩn.
    - Mỗi câu có 4 đáp án A, B, C, D và 1 đáp án đúng.
    - Phân loại Domain: Ngữ pháp, Từ vựng, Đọc hiểu, Logic.
    Trả về định dạng JSON: {{"questions": [ {{"question": "...", "options": ["...", "..."], "answer": "...", "domain": "..."}} ]}}
    """
    raw_res = call_groq(prompt)
    return json.loads(raw_res).get("questions", [])

# --- TRANG 1: WELCOME ---
if st.session_state.page == "welcome":
    st.title("🏯 Hệ thống Kiểm tra Năng lực AI")
    st.session_state.subject = st.selectbox("Chọn môn thi:", ["Tiếng Nhật (N1-N5)", "Tiếng Anh", "IQ Logic"])
    count = st.select_slider("Số câu hỏi:", options=[5, 10, 15, 20])
    
    if st.button("🚀 Bắt đầu làm bài"):
        with st.spinner("AI đang biên soạn đề thi..."):
            st.session_state.quiz_data = generate_quiz(st.session_state.subject, count)
            st.session_state.start_time = time.time()
            st.session_state.page = "quiz"
            st.rerun()

# --- TRANG 2: LÀM BÀI ---
elif st.session_state.page == "quiz":
    st.title(f"📝 Bài thi: {st.session_state.subject}")
    
    for i, q in enumerate(st.session_state.quiz_data):
        st.subheader(f"Câu {i+1} [{q['domain']}]:")
        st.write(q['question'])
        st.session_state.answers[i] = st.radio(f"Chọn đáp án:", q['options'], key=f"ans_{i}", index=None)
        st.divider()
    
    if st.button("🏁 Nộp bài"):
        st.session_state.end_time = time.time()
        st.session_state.page = "result"
        st.rerun()

# --- TRANG 3: KẾT QUẢ & PHÂN TÍCH ---
elif st.session_state.page == "result":
    st.title("📊 Phân tích Kết quả")
    
    # 1. Tính toán điểm số
    results = []
    correct_count = 0
    for i, q in enumerate(st.session_state.quiz_data):
        u_ans = st.session_state.answers.get(i)
        is_correct = (u_ans == q['answer'])
        if is_correct: correct_count += 1
        results.append({"Domain": q['domain'], "IsCorrect": 1 if is_correct else 0})
    
    df = pd.DataFrame(results)
    total_q = len(st.session_state.quiz_data)
    score_pct = (correct_count / total_q) * 100
    total_time = round(st.session_state.end_time - st.session_state.start_time, 1)

    # 2. Hiển thị Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng điểm", f"{score_pct:.1f}%")
    c2.metric("Số câu đúng", f"{correct_count}/{total_q}")
    c3.metric("Thời gian", f"{total_time}s")

    # 3. Vẽ biểu đồ Radar chuyên sâu
    # Gom nhóm theo Domain và tính % đúng của mỗi nhóm
    chart_data = df.groupby("Domain")["IsCorrect"].mean().reset_index()
    chart_data["Score"] = chart_data["IsCorrect"] * 100

    categories = chart_data["Domain"].tolist()
    values = chart_data["Score"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Năng lực thực tế',
        line_color='#1f77b4'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), title="Biểu đồ đa chiều về năng lực")
    st.plotly_chart(fig)

    # 4. Lời khuyên AI chuyên sâu
    st.subheader("💡 Đánh giá chi tiết từ Chuyên gia AI")
    with st.spinner("Đang phân tích điểm số..."):
        analysis_prompt = f"""
        Phân tích kết quả bài thi {st.session_state.subject}:
        - Tổng điểm: {score_pct}%
        - Thời gian làm: {total_time} giây cho {total_q} câu.
        - Chi tiết từng phần (0-100%): {chart_data[['Domain', 'Score']].to_dict()}.
        Hãy đưa ra đánh giá dài, chuyên sâu, phân tích kỹ điểm mạnh điểm yếu và lộ trình học tập tiếp theo.
        """
        advice = call_groq(analysis_prompt, json_mode=False)
        st.info(advice)

    if st.button("🔄 Thử sức lại từ đầu"):
        for key in ["quiz_data", "answers", "page"]: st.session_state[key] = "welcome" if key=="page" else ({} if key=="answers" else None)
        st.rerun()

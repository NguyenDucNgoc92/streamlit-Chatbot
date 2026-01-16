import streamlit as st
import pandas as pd
import kagglehub
import plotly.express as px
import os

# --- CẤU HÌNH ---
st.set_page_config(page_title="Universal Data Analyzer", layout="wide")
st.title("📊 Phân tích Dữ liệu Đa nguồn")

# --- CHỌN NGUỒN DỮ LIỆU ---
st.sidebar.header("Cấu hình Nguồn dữ liệu")
source_type = st.sidebar.radio(
    "Chọn nguồn dữ liệu:",
    ("Tải file lên (CSV/Excel)", "Nhập Kaggle Dataset ID", "Dữ liệu mẫu (Premier League)")
)

df = None

# --- XỬ LÝ NGUỒN DỮ LIỆU ---
if source_type == "Tải file lên (CSV/Excel)":
    uploaded_file = st.sidebar.file_uploader("Chọn file", type=['csv', 'xlsx'])
    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

elif source_type == "Nhập Kaggle Dataset ID":
    kaggle_id = st.sidebar.text_input("Dán ID Kaggle (VD: ajaxianazarenka/premier-league)", "")
    if kaggle_id:
        try:
            with st.spinner("Đang tải dữ liệu từ Kaggle..."):
                path = kagglehub.dataset_download(kaggle_id)
                # Tự động tìm file CSV đầu tiên trong thư mục tải về
                files = [f for f in os.listdir(path) if f.endswith('.csv')]
                if files:
                    df = pd.read_csv(os.path.join(path, files[0]))
                    st.sidebar.success(f"Đã tải file: {files[0]}")
                else:
                    st.sidebar.error("Không tìm thấy file CSV trong Dataset này.")
        except Exception as e:
            st.sidebar.error(f"Lỗi Kaggle: {e}")

else: # Dữ liệu mặc định
    path = kagglehub.dataset_download("ajaxianazarenka/premier-league")
    df = pd.read_csv(os.path.join(path, "premier-league.csv"))

# --- GIAO DIỆN PHÂN TÍCH ---
if df is not None:
    st.divider()
    
    # 1. Xem trước dữ liệu
    with st.expander("👀 Xem bảng dữ liệu gốc"):
        st.dataframe(df, use_container_width=True)

    # 2. Thống kê cơ bản
    st.subheader("📈 Thống kê tổng quan")
    col1, col2, col3 = st.columns(3)
    col1.metric("Số dòng", df.shape[0])
    col2.metric("Số cột", df.shape[1])
    col3.metric("Số ô trống", df.isnull().sum().sum())

    # 3. Tạo biểu đồ tùy chỉnh
    st.subheader("🎨 Trình tạo biểu đồ thông minh")
    all_columns = df.columns.tolist()
    
    c1, c2, c3 = st.columns(3)
    x_axis = c1.selectbox("Chọn trục X (Phân loại)", all_columns)
    y_axis = c2.selectbox("Chọn trục Y (Số liệu)", all_columns)
    chart_type = c3.selectbox("Loại biểu đồ", ["Cột (Bar)", "Đường (Line)", "Vùng (Area)", "Tán xạ (Scatter)"])

    try:
        if chart_type == "Cột (Bar)":
            fig = px.bar(df, x=x_axis, y=y_axis, color=x_axis, title=f"{y_axis} theo {x_axis}")
        elif chart_type == "Đường (Line)":
            fig = px.line(df, x=x_axis, y=y_axis, title=f"Xu hướng {y_axis}")
        elif chart_type == "Vùng (Area)":
            fig = px.area(df, x=x_axis, y=y_axis, title=f"Mật độ {y_axis}")
        else:
            fig = px.scatter(df, x=x_axis, y=y_axis, color=x_axis, title=f"Tương quan {x_axis} và {y_axis}")
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Không thể vẽ biểu đồ với các cột đã chọn. Hãy chọn cột chứa dữ liệu số! (Lỗi: {e})")

else:
    st.info("💡 Vui lòng cung cấp dữ liệu từ thanh bên trái để bắt đầu phân tích.")

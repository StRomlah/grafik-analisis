import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from streamlit_lottie import st_lottie
import requests

# Fungsi untuk memuat animasi Lottie
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load environment variables
load_dotenv()

# Konfigurasi untuk Azure OpenAI API dari file .env
azure_endpoint = os.getenv('AZURE_ENDPOINT')
api_key = os.getenv('API_KEY')
api_version = os.getenv('API_VERSION')

# Menginisialisasi klien Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

# Fungsi untuk membaca file berdasarkan tipe
def load_file(uploaded_file):
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file)
        elif file_extension == 'json':
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format")
            return None
        return df
    return None

# Fungsi untuk membuat grafik
def create_charts(chart_type, data_frame, x_col, y_col):
    fig = None
    if chart_type == 'Line Chart':
        fig = px.line(data_frame, x=x_col, y=y_col, title='Line Chart')
    elif chart_type == 'Bar Chart':
        fig = px.bar(data_frame, x=x_col, y=y_col, title='Bar Chart')
    elif chart_type == 'Pie Chart':
        fig = px.pie(data_frame, names=x_col, values=y_col, title='Pie Chart')
    elif chart_type == 'Scatter Plot':
        fig = px.scatter(data_frame, x=x_col, y=y_col, title='Scatter Plot')
    elif chart_type == 'Area Chart':
        fig = px.area(data_frame, x=x_col, y=y_col, title='Area Chart')
    elif chart_type == 'Stacked Bar Chart':
        fig = px.bar(data_frame, x=x_col, y=y_col, title='Stacked Bar Chart', barmode='stack')
    elif chart_type == 'Waterfall Chart':
        measure = ['absolute'] + ['relative' for _ in range(1, len(data_frame[y_col])-1)] + ['total']
        fig = go.Figure(go.Waterfall(
            x=data_frame[x_col],
            y=data_frame[y_col],
            measure=measure,
            text=[f"{v:,.0f}" for v in data_frame[y_col]],
            textposition="outside",
            connector=dict(line=dict(color='rgb(63, 63, 63)', width=2)),
        ))
        fig.update_layout(title="Waterfall Chart")
    elif chart_type == 'Bubble Chart':
        fig = px.scatter(data_frame, x=x_col, y=y_col, size=y_col, color=y_col, hover_name=x_col, title='Bubble Chart')
    elif chart_type == 'Tree Map':
        fig = px.treemap(data_frame, path=[x_col], values=y_col, title='Tree Map')
    elif chart_type == 'Gauge Chart':
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=data_frame[x_col].iloc[0],
            title={'text': f"Gauge Chart: {x_col} vs {y_col}"},
            delta={'reference': data_frame[y_col].iloc[0]},
            gauge={
                'axis': {'range': [0, max(data_frame[x_col].iloc[0], data_frame[y_col].iloc[0]) * 1.2]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, data_frame[y_col].iloc[0]], 'color': "lightgray"},
                    {'range': [data_frame[y_col].iloc[0], data_frame[x_col].iloc[0]], 'color': "gray"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': data_frame[x_col].iloc[0]}}))
        fig.update_layout(title=f"{x_col} vs {y_col}")
    else:
        st.error("Chart type not recognized.")
        return None
    return fig

# Fungsi untuk menghasilkan narasi dari AI
def generate_narrative(system_prompt, user_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return response.choices[0].message.content

# Gaya CSS untuk tampilan profesional dan custom button
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5em;
            font-weight: bold;
            color: #2E86C1;
            text-align: center;
            margin-bottom: 20px;
        }
        .main-subheader {
            font-size: 1.5em;
            font-weight: bold;
            color: #333333;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .main-footer {
            font-size: 0.9em;
            color: #AAAAAA;
            text-align: center;
            margin-top: 20px;
        }
        .sidebar .sidebar-content {
            background-color: #F0F2F6;
            padding: 10px;
            border-radius: 5px;
        }
        .narrative-container {
            background-color: #F9F9F9;
            border: 1px solid #E0E0E0;
            border-radius: 5px;
            padding: 15px;
            margin-top: 10px;
        }
        .custom-button {
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            text-decoration: none;
            background-color: #2E86C1;
            color: white;
            border: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .custom-button:hover {
            background-color: #1F618D;
        }
    </style>
""", unsafe_allow_html=True)

# URL animasi Lottie
lottie_animation_url = "https://lottie.host/40eb321b-edf1-42f0-b982-a0c33c23b9ec/TbobicdLp3.json"
lottie_animation = load_lottieurl(lottie_animation_url)

# Judul aplikasi
st.markdown('<div class="main-header">Mengkonversi Insight dalam Chart Menjadi Narasi</div>', unsafe_allow_html=True)

# Menampilkan animasi Lottie di bawah judul
if lottie_animation:
    st_lottie(lottie_animation, height=150, key="animation")

# Bagian sidebar untuk upload file
st.sidebar.title("Upload Data")
uploaded_file = st.sidebar.file_uploader("Pilih File", type=["csv", "xls", "xlsx", "json"])

# Jika tidak ada file yang diunggah, tampilkan pesan di sidebar
if uploaded_file is None:
    st.sidebar.info("Please upload a file.")

df = load_file(uploaded_file)

if df is not None:
    # Tampilkan data
    st.markdown('<div class="main-subheader">Data Preview</div>', unsafe_allow_html=True)
    st.write(df.head())

    # Sidebar untuk pengaturan grafik
    st.sidebar.title("Pengaturan Grafik")
    x_col = st.sidebar.selectbox("Grafik Kolom X", df.columns)
    y_col = st.sidebar.selectbox("Grafik Kolom Y", df.columns)
    chart_type = st.sidebar.selectbox(
        "Pilih Tipe Chart:",
        options=["Line Chart", "Bar Chart", "Pie Chart", "Scatter Plot", "Area Chart", "Stacked Bar Chart", "Waterfall Chart", "Bubble Chart", "Tree Map", "Gauge Chart"]
    )

    # Tombol hasilkan chart dengan style custom
    generate_chart = st.sidebar.button("Hasilkan Chart", key="generate_chart")
    if generate_chart:
        with st.spinner("Membuat Chart..."):
            fig = create_charts(chart_type, df, x_col, y_col)
            st.session_state['fig'] = fig

    if 'fig' in st.session_state:
        st.markdown('<div class="main-subheader">Generated Chart</div>', unsafe_allow_html=True)
        fig = st.session_state['fig']
        if isinstance(fig, go.Figure):
            st.plotly_chart(fig)
        else:
            st.pyplot(fig)

    # Input teks untuk prompt pengguna
    st.markdown('<div class="main-subheader">Generate Narrative</div>', unsafe_allow_html=True)
    user_prompt_content = st.text_area("Masukkan prompt untuk AI:", "")

    # Tombol hasilkan insight dengan style custom
    generate_insight = st.button("Hasilkan Insight", key="generate_insight")
    if generate_insight:
        if user_prompt_content:
            with st.spinner("Membuat Insight..."):
                variable_A = df[x_col].tolist()
                variable_B = df[y_col].tolist()
                system_prompt = f'''
                Kamu adalah storyteller AI yang bertugas untuk menganalisis dan menginterpretasikan visualisasi data. 
                Data yang akan kamu analisis memiliki kolom {x_col} sebagai sumbu x dan {y_col} sebagai sumbu y. 
                Grafik yang digunakan untuk visualisasi adalah "{chart_type}". Tugas kamu adalah untuk mengubah informasi kompleks dari grafik 
                menjadi narasi yang jelas dan mudah dipahami, seperti yang ditemukan dalam infografis, sehingga dapat dengan mudah 
                dipahami oleh orang yang tidak memiliki latar belakang teknis.
                '''
                full_prompt = system_prompt + user_prompt_content
                insight = generate_narrative(system_prompt, user_prompt_content)
                st.markdown('<div class="main-subheader">Insight dari AI:</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="narrative-container">{insight}</div>', unsafe_allow_html=True)
        else:
            st.error("Please enter a prompt for the AI.")
else:
    # Jangan tampilkan pesan "Please upload a file." di bawah animasi
    pass

# Footer aplikasi
st.markdown('<div class="main-footer">Developed by [Group 6 - Tetris] - © 2024</div>', unsafe_allow_html=True)

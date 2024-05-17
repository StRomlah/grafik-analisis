import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from openai import OpenAI
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan dari file .env
load_dotenv()
azure_endpoint = os.getenv('AZURE_ENDPOINT')
api_key = os.getenv('API_KEY')
api_version = os.getenv('API_VERSION')

# Setup client Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

# Fungsi untuk menghasilkan narasi dari AI
def generate_narrative(prompt):
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return response.choices[0].message.content

# Title
st.title("Konversi Informasi Penting dalam Chart Menjadi Narasi")

# Fungsi untuk memuat data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        st.success("Data berhasil dimuat.")
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {str(e)}")
        return None

# Fungsi untuk membuat grafik berdasarkan pilihan pengguna
def create_chart(dataframe, chart_type, x_col, y_col)#, color_theme, year=None):
    if chart_type == 'Bar Chart':
        uniform_color = ['#1f77b4']  # Semua bar akan berwarna biru
        
        # Contoh warna yang berbeda untuk setiap bar
        different_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        fig = px.bar(dataframe, x=x_col, y=y_col, color_discrete_sequence=uniform_color)#, color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Bar Chart",
            xaxis_title=x_col,
            yaxis_title=y_col,
            #template='plotly_white',
            font=dict(color='black')
        )
        return fig
    elif chart_type == 'Line Chart':
        fig = px.line(dataframe, x=x_col, y=y_col, color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Line Chart",
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_white',
            font=dict(color='black')
        )
        return fig
    elif chart_type == 'Pie Chart':
        fig = px.pie(dataframe, names=x_col, values=y_col, color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Pie Chart",
            template='plotly_white',
            font=dict(color='black')
        )
        return fig
    elif chart_type == 'Scatter Plot':
        fig = px.scatter(dataframe, x=x_col, y=y_col, color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Scatter Plot",
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_white',
            font=dict(color='black')
        )
        return fig
    elif chart_type == 'Area Chart':
        fig = px.area(dataframe, x=x_col, y=y_col, color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Area Chart",
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_white',
            font=dict(color='black')
        )
        return fig
    elif chart_type == 'Double Line Chart':
        y_cols = st.multiselect('Pilih kolom sumbu Y kedua', dataframe.columns, key="y_col_2")
        if len(y_cols) > 1:
            fig = px.line(dataframe, x=x_col, y=y_cols, color_discrete_sequence=color_theme)
            fig.update_layout(
                title="Double Line Chart",
                xaxis_title=x_col,
                yaxis_title=", ".join(y_cols),
                template='plotly_white',
                font=dict(color='black')
            )
            return fig
    elif chart_type == 'Waterfall Chart':
        return create_waterfall(dataframe, year, 'Monthly' if 'Month Name' in dataframe.columns else 'Yearly')
    elif chart_type == 'Tree Map':
        fig = px.treemap(dataframe, path=[x_col], values=y_col, color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Tree Map",
            template='plotly_white',
            font=dict(color='black')
        )
        return fig
    elif chart_type == 'Bubble Chart':
        fig = px.scatter(dataframe, x=x_col, y=y_col, size=dataframe[y_col], color_discrete_sequence=color_theme)
        fig.update_layout(
            title="Bubble Chart",
            xaxis_title=x_col,
            yaxis_title=y_col,
            template='plotly_white',
            font=dict(color='black')
        )
        return fig
    else:
        return None
# Menentukan tema warna yang akan digunakan
color_theme = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# Fungsi untuk membuat grafik waterfall
def create_waterfall(data, year, profit_type):
    if profit_type == 'Monthly' and year is not None:
        filtered_data = data[data['Order Year'] == year]
        filtered_data['Period'] = filtered_data['Month Name']
    else:
        filtered_data = data.groupby('Order Year').agg({'Profit': 'sum'}).reset_index()
        filtered_data['Period'] = filtered_data['Order Year'].astype(str)
    
    fig = go.Figure(go.Waterfall(
        x=filtered_data['Period'],
        y=filtered_data['Profit'],
        measure=['relative'] * len(filtered_data),
        increasing=dict(marker_color='green'),
        decreasing=dict(marker_color='red'),
        totals=dict(marker_color='blue'),
    ))
    
    fig.update_layout(
        title="Waterfall Chart of Profit",
        xaxis_title='Period',
        yaxis_title='Profit',
        template='plotly_white'
    )
    return fig

# Fungsi untuk membuat deskripsi data yang otomatis hanya berisi informasi data pada chart
def create_data_description(dataframe, x_col, y_col, chart_type, year=None):
    if chart_type == 'Waterfall Chart':
        if 'Order Month' in dataframe.columns:
            # Menghitung total profit atau sales bulanan untuk tahun yang dipilih
            monthly_data = dataframe[dataframe['Order Year'] == year].groupby(['Order Month'])[y_col].sum().reset_index()
            monthly_data['Measure'] = 'relative'
            monthly_data.loc[0, 'Measure'] = 'absolute'
            annual_total = monthly_data[y_col].sum()
            total_row = pd.DataFrame({'Order Month': ['Total'], y_col: [annual_total], 'Measure': ['total']})
            monthly_data = pd.concat([monthly_data, total_row])

            # Mengurutkan DataFrame berdasarkan Order Month
            month_order = list(range(1, 13)) + ['Total']
            monthly_data['Order Month'] = pd.Categorical(monthly_data['Order Month'], categories=month_order, ordered=True)
            monthly_data = monthly_data.sort_values('Order Month')

            summary_dict = monthly_data.to_dict(orient='list')
        else:
            # Menghitung total profit atau sales tahunan
            annual_data = dataframe.groupby(['Order Year'])[y_col].sum().reset_index()
            annual_data['Measure'] = 'relative'
            annual_data.loc[0, 'Measure'] = 'absolute'
            total_row = pd.DataFrame({'Order Year': ['Total'], y_col: [annual_data[y_col].sum()], 'Measure': ['total']})
            annual_data = pd.concat([annual_data, total_row])

            summary_dict = annual_data.to_dict(orient='list')
    else:
        summary = dataframe.groupby(x_col)[y_col].sum().reset_index()
        summary_dict = summary.to_dict(orient='list')
    return summary_dict

# Upload File Data
uploaded_file = st.file_uploader("Pilih file CSV")
dataframe = None
if uploaded_file is not None:
    file_path = uploaded_file.name
    dataframe = load_data(file_path)
    if dataframe is not None:
        st.dataframe(dataframe.head())
        st.session_state['current_df'] = dataframe
        st.session_state['dataset_name'] = file_path

if dataframe is not None:
    dataset_name = st.session_state['dataset_name']
    chart_type = st.selectbox('Pilih jenis grafik', [
        'Bar Chart', 'Line Chart', 'Pie Chart', 'Scatter Plot', 'Area Chart',
        'Double Line Chart', 'Waterfall Chart', 'Tree Map', 'Bubble Chart'
    ], key="chart_type")

    x_col = st.selectbox('Pilih kolom sumbu X', dataframe.columns, key="x_col")
    y_col = st.selectbox('Pilih kolom sumbu Y', dataframe.columns, key="y_col")
    year = None
    if chart_type == 'Waterfall Chart' and 'Order Year' in dataframe.columns:
        year = st.selectbox('Pilih Tahun', dataframe['Order Year'].unique(), key="year")



    # Create and display chart
    if st.button('Buat Grafik', key="create_chart"):
        chart = create_chart(dataframe, chart_type, x_col, y_col, color_theme, year)
        if chart:
            st.session_state['chart'] = chart
        else:
            st.warning("Grafik tidak valid. Silakan konfigurasikan opsi grafik Anda dan tekan 'Buat Grafik'.")

if 'chart' in st.session_state:
    st.header("Generated Chart")
    st.plotly_chart(st.session_state['chart'])

# User Query Input
st.header("Generate Insight")
user_query = st.text_area("Masukkan pertanyaan Anda di sini...", key="user_question")
if st.button("Hasilkan Narasi", key="generate_narrative"):
    if user_query and 'current_df' in st.session_state:
        dataset_name = st.session_state['dataset_name']
        chart_type = st.session_state.get('chart_type', 'Unknown Chart Type')
        x_col = st.session_state['x_col']
        y_col = st.session_state['y_col']
        year = None
        if chart_type == 'Waterfall Chart' and 'Order Month' in st.session_state['current_df'].columns:
            year = st.session_state['year']
        description_of_data = create_data_description(st.session_state['current_df'], x_col, y_col, chart_type, year)
        
        # System prompt
        system_prompt = (
            "Anda adalah AI yang bertugas untuk menganalisis data dan memberikan insight yang berguna. "
            "Berikut adalah data yang digunakan untuk membuat chart: "
            f"{description_of_data}. "
            "Berdasarkan informasi tersebut, berikan penjelasan mendalam tentang bagaimana elemen-elemen ini berinteraksi "
            "dan berikan insightnya dalam bentuk narasi storytelling yang mudah dipahami."
        )
        
        # User prompt
        user_prompt = user_query
        
        if user_prompt:
            narrative = generate_narrative(f"{system_prompt} {user_prompt}")
            st.write("## Narasi yang Dihasilkan AI")
            st.write(narrative)
        else:
            st.error("Masukkan pertanyaan untuk menghasilkan narasi.")
    else:
        st.error("Pastikan data telah dimuat dan pertanyaan telah dimasukkan.")

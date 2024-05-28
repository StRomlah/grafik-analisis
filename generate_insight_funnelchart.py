import pandas as pd
import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

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

def buat_insight_dari_grafik(file_path, stages_col, values_col, chart_title):
    # Baca data dari file CSV
    data = pd.read_csv(file_path)
    
    # Konversi data ke Pandas DataFrame
    df = pd.DataFrame(data)
    
    # Konversi data ke format JSON
    data_json = df.to_json(orient="records", lines=True)

    # Deskripsi chart dan kode Python untuk membuat chart
    chart_description = f"""
    Berikut adalah kode Python untuk membuat diagram funnel:

    import plotly.graph_objects as go

    stages = {df[stages_col].tolist()}
    values = {df[values_col].tolist()}

    fig = go.Figure(go.Funnel(
        y = stages,
        x = values,
        textinfo = "value+percent initial"
    ))

    fig.update_layout(title_text="{chart_title}", font_size=10)
    fig.show()
    """

    # Definisikan sistem prompt (termasuk data dan instruksi umum)
    system_prompt = f"""
Anda adalah seorang analis data AI. Tugas Anda adalah menganalisis data penjualan yang diberikan dalam bentuk grafik dan menghasilkan insight dalam bentuk narasi storytelling yang cocok untuk sebuah infografis.

Berikut adalah data penjualan yang perlu Anda analisis:
{data_json}

Data ini memiliki kolom dan value sebagai berikut:
- {stages_col} yang mewakili tahapan funnel
- {values_col} yang mewakili jumlah pengunjung di setiap tahap

Berikut adalah deskripsi chart yang dimaksud dan kode Python untuk membuatnya:
{chart_description}

Pastikan analisis Anda didasarkan pada perhitungan matematis yang akurat untuk memastikan tidak ada kesalahan atau kekeliruan dalam interpretasi data. Berikan narasi yang mudah dipahami dan menarik agar dapat dengan mudah dipahami oleh orang yang tidak memiliki latar belakang teknis.
"""
    
    # Definisikan prompt pengguna (instruksi atau pertanyaan spesifik pengguna)
    user_prompt = f"""
Buatlah narasi yang berisi analisis harus mencakup:
- Identifikasi tahapan dengan jumlah penurunan terbesar.
- Bandingkan jumlah pengunjung antara tahapan.
- Bagaimana perbandingan jumlah pengunjung antara setiap tahap.
- Identifikasi faktor-faktor yang mungkin menyebabkan variasi dalam distribusi.
- Berikan rekomendasi berdasarkan temuan.
"""

    # Menghasilkan narasi dari AI
    narrative = generate_narrative(system_prompt, user_prompt)

    return narrative

# File CSV yang diunggah oleh pengguna
data_file = r"C:\Users\IYOM\myenvir\funnel_chart_stages.csv"  # Ganti dengan path yang benar

# Kolom yang ada di dataset pengguna
stages_col = "Stages"  # Nama kolom untuk tahap funnel
values_col = "Values"  # Nama kolom untuk nilai di setiap tahap

# Judul grafik
chart_title = "Funnel Chart: Proses Konversi Penjualan"  # Ganti dengan judul yang sesuai

# Hasilkan insight untuk data funnel chart
insight_funnel = buat_insight_dari_grafik(data_file, stages_col, values_col, chart_title)
print("Insight Funnel Chart:\n", insight_funnel)

# Simpan output ke file teks
output_file = os.path.join(os.path.dirname(data_file), "insight_output_funnel.txt")
with open(output_file, "w") as file:
    file.write("Insight Funnel Chart:\n")
    file.write(insight_funnel)

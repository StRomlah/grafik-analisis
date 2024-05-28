import pandas as pd
import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Fungsi untuk menghasilkan narasi dari AI
def menghasilkan_narasi(prompt_sistem, prompt_pengguna):
    pesan = [
        {"role": "system", "content": prompt_sistem},
        {"role": "user", "content": prompt_pengguna}
    ]
    respons = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=pesan,
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return respons.choices[0].message.content

# Memuat variabel lingkungan
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

def menghasilkan_insight_dari_chart(file_path, kolom_total, kolom_target, judul_chart):
    # Baca data dari file CSV
    data = pd.read_csv(file_path)
    
    # Konversi data ke Pandas DataFrame
    df = pd.DataFrame(data)
    
    # Konversi data ke format JSON
    data_json = df.to_json(orient="records", lines=True)

    # Deskripsi chart dan kode Python untuk membuat chart
    deskripsi_chart = f"""
    Berikut adalah kode Python untuk membuat grafik gauge:

    import plotly.graph_objects as go

    total = {df[kolom_total].iloc[0]}
    target = {df[kolom_target].iloc[0]}

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total,
        delta = {{'reference': target}},
        gauge = {{
            'axis': {{'range': [0, target * 1.2]}},
            'steps': [
                {{'range': [0, target * 0.5], 'color': "lightgray"}},
                {{'range': [target * 0.5, target], 'color': "gray"}}],
            'threshold': {{
                'line': {{'color': "red", 'width': 4}},
                'thickness': 0.75,
                'value': target}},
        title = {{'text': "{judul_chart}"}}
    ))

    fig.show()
    """

    # Definisikan sistem prompt (termasuk data dan instruksi umum)
    prompt_sistem = f"""
Anda adalah seorang analis data AI. Tugas Anda adalah menganalisis data penjualan yang diberikan dalam bentuk grafik dan menghasilkan insight dalam bentuk narasi storytelling yang cocok untuk sebuah infografis.

Berikut adalah data penjualan yang perlu Anda analisis:
{data_json}

Data ini memiliki kolom dan value sebagai berikut:
- {kolom_total} yang mewakili nilai total yang telah didapat
- {kolom_target} yang mewakili nilai target yang ingin dicapai

Berikut adalah deskripsi chart yang dimaksud dan kode Python untuk membuatnya:
{deskripsi_chart}

Pastikan analisis Anda didasarkan pada perhitungan matematis yang akurat untuk memastikan tidak ada kesalahan atau kekeliruan dalam interpretasi data. Berikan narasi yang mudah dipahami dan menarik agar dapat dengan mudah dipahami oleh orang yang tidak memiliki latar belakang teknis.
"""
    
    # Definisikan prompt pengguna (instruksi atau pertanyaan spesifik pengguna)
    prompt_pengguna = f"""
Buatlah narasi yang berisi analisis yang harus mencakup:
- Perbandingan total penjualan terhadap target penjualan tahunan.
- Identifikasi seberapa dekat atau jauh total penjualan dari target.
- Interpretasi visual dari gauge chart terkait pencapaian penjualan.
- Faktor-faktor yang mungkin mempengaruhi pencapaian penjualan.
- Rekomendasi strategi untuk mencapai atau melampaui target penjualan.
"""

    # Menghasilkan narasi dari AI
    narasi = menghasilkan_narasi(prompt_sistem, prompt_pengguna)

    return narasi

# File CSV yang diunggah oleh pengguna
file_data = r"C:\Users\IYOM\myenvir\df_gauge.csv"  # Ganti dengan path yang benar

# Kolom yang ada di dataset pengguna
kolom_total = "total_sales"  # Pilih kolom untuk nilai total / nilai yang telah dicapai
kolom_target = "target_sales"  # Pilih kolom untuk nilai target 

# Judul grafik
judul_chart = "Gauge Chart: Total Sales vs Target Sales"  # Ganti dengan judul yang sesuai

# Hasilkan insight untuk data gauge chart
insight_gauge = menghasilkan_insight_dari_chart(file_data, kolom_total, kolom_target, judul_chart)
print("Insight Gauge Chart:\n", insight_gauge)

# Simpan output ke file teks
output_file = os.path.join(os.path.dirname(file_data), "insight_output_gauge.txt")
with open(output_file, "w") as file:
    file.write("Insight Gauge Chart:\n")
    file.write(insight_gauge)

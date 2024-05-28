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

def buat_insight_dari_grafik(file_path, sumbu_x, sumbu_y, nilai, judul):
    # Baca data dari file CSV
    data = pd.read_csv(file_path)
    
    # Konversi data ke Pandas DataFrame
    df = pd.DataFrame(data)
    #print("Dataframe:\n", df.head())  # Tambahkan pemeriksaan untuk melihat isi dataframe
    
    # Konversi data ke format JSON
    data_json = df.to_json(orient="records", lines=True)
    #print("Data JSON:\n", data_json)  # Tambahkan pemeriksaan untuk melihat data JSON

    # Deskripsi chart dan kode Python untuk membuat chart
    chart_description = f"""
    Berikut adalah kode Python untuk membuat diagram sankey:

    import plotly.graph_objects as go

    labels = {df[sumbu_x].unique().tolist() + df[sumbu_y].unique().tolist()}
    source = {df[sumbu_x].apply(lambda x: df[sumbu_x].unique().tolist().index(x)).tolist()}
    target = {df[sumbu_y].apply(lambda x: df[sumbu_y].unique().tolist().index(x) + len(df[sumbu_x].unique().tolist())).tolist()}
    value = {df[nilai].tolist()}

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

    fig.update_layout(title_text="{judul}", font_size=10)
    fig.show()
    """

    # Definisikan sistem prompt (termasuk data dan instruksi umum)
    sistem_prompt = f"""
Anda adalah seorang data alais AI. Tugas Anda adalah menganalisis data penjualan yang diberikan dalam bentuk grafik dan menghasilkan insight dalam bentuk narasi storytelling yang cocok untuk sebuah infografis.

Berikut adalah data penjualan yang perlu Anda analisis:
{data_json}

Data ini memiliki kolom dan value sebagai berikut:
- varibael A : {sumbu_x} pada sumbu X
- variabel B: {sumbu_y} pada sumbu Y
- variabel C: {nilai} yang bernilai value


Berikut adalah deskripsi chart yang dimaksud dan kode Python untuk membuatnya:
{chart_description}

Pastikan analisis Anda didasarkan pada perhitungan matematis yang akurat untuk memastikan tidak ada kesalahan atau kekeliruan dalam interpretasi data. Berikan narasi yang mudah dipahami dan menarik agar dapat dengan mudah dipahami oleh orang yang tidak memiliki latar belakang teknis.
"""
    
    # Definisikan prompt pengguna (instruksi atau pertanyaan spesifik pengguna)
    prompt_pengguna = f"""
Berikan analisis harus mencakup:
- Identifikasi aliran penjualan kategori terbesar dan terkecil.
- Bandingkan jumlah penjualan antara kategori.
- Bagaimana perbandingan penjualan kategori antar kota.
- Identifikasi faktor-faktor yang mungkin menyebabkan variasi dalam distribusi.
- Berikan rekomendasi berdasarkan temuan.
"""

    # Menghasilkan narasi dari AI
    narasi = generate_narrative(sistem_prompt, prompt_pengguna)

    return narasi

# File CSV yang diunggah oleh pengguna
data_file =  r"C:\Users\IYOM\myenvir\df_sankey.csv"  # Ganti dengan path yang benar

# Kolom yang ada di dataset pengguna
sumbu_x = "city"  # Ganti dengan nama kolom yang sesuai di dataset Anda
sumbu_y = "product_category"  # Ganti dengan nama kolom yang sesuai di dataset Anda
nilai = "value"  # Ganti dengan nama kolom yang sesuai di dataset Anda

# Judul grafik
judul_grafik = "Aliran Penjualan Produk Berdasarkan Kota dan Kategori" # Ganti dengan judul yang sesuai

# Hasilkan insight untuk data penjualan
insight_sankey = buat_insight_dari_grafik(data_file, sumbu_x, sumbu_y, nilai, judul_grafik)
print("Insight Grafik Sankey:\n", insight_sankey)

# Simpan output ke file teks
output_file = os.path.join(os.path.dirname(data_file), "insight_output_sankey.txt")
with open(output_file, "w") as file:
    file.write("Insight Grafik Sankey:\n")
    file.write(insight_sankey)

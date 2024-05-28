import pandas as pd
import matplotlib.pyplot as plt
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

def buat_insight_dari_grafik(data, label_x, label_y, judul, jenis_grafik='pie'):
    # Konversi data ke Pandas DataFrame
    df = pd.DataFrame(data)
    
    # Buat plot dari data
    plt.figure(figsize=(10, 6))
    
    if jenis_grafik == 'pie':
        plt.pie(df[label_y], labels=df[label_x], autopct='%1.1f%%')
    
    plt.title(judul)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
    
    # Konversi data sumbu x dan y ke format JSON
    data_json = json.dumps({
        label_x: data[label_x],
        label_y: data[label_y]
    })

    # Definisikan sistem prompt (termasuk data dan instruksi umum)
    sistem_prompt = f"""
Anda adalah seorang analis data AI. Tugas Anda adalah menganalisis data yang diberikan dan menghasilkan insight dalam bentuk narasi yang cocok untuk sebuah infografis.
Berikut adalah data penjualan yang perlu Anda analisis:
{data_json}

Grafik ini adalah pie chart yang menunjukkan distribusi "{label_y}" berdasarkan "{label_x}" dengan judul "{judul}". Analisis harus mencakup:
- Sebutkan jumlah dan persentase kategori dengan proporsi terbesar dan terkecil
- Bandingkan perbedaan atau selisih jumlah dan persentase antar kategori
- Identifikasi faktor-faktor yang mungkin menyebabkan variasi dalam distribusi
- Berikan rekomendasi berdasarkan temuan

Pastikan analisis Anda didasarkan pada perhitungan matematis yang akurat untuk memastikan tidak ada kesalahan atau kekeliruan dalam interpretasi data. Berikan narasi yang mudah dipahami dan menarik agar dapat dengan mudah dipahami oleh orang yang tidak memiliki latar belakang teknis.
"""
    
    # Definisikan prompt pengguna (instruksi atau pertanyaan spesifik pengguna)
    prompt_pengguna = "Buatlah narasi insight dari data dan visualisasi di atas."

    # Menghasilkan narasi dari AI
    narasi = generate_narrative(sistem_prompt, prompt_pengguna)

    return narasi

# Baca data dari file CSV
data_file = "C:/Users/IYOM/myenvir/city_sales.csv"
data = pd.read_csv(data_file)

# Konversi data ke format yang sesuai
data_dict = {
    "city": data["city"].tolist(),
    "sales_amount": data["sales_amount"].tolist()
}

# Hasilkan insight untuk pie chart
judul_grafik = "Distribusi Penjualan Berdasarkan Kota"
insight_pie = buat_insight_dari_grafik(data_dict, "city", "sales_amount", "Sales Berdasarkan Kota", jenis_grafik='pie')
print("Insight Grafik Pie:\n", insight_pie)

# Simpan output ke file teks
output_file = os.path.join(os.path.dirname(data_file), "insight_output_piechart.txt")
with open(output_file, "w") as file:
    file.write("Insight Grafik Pie:\n")
    file.write(insight_pie)

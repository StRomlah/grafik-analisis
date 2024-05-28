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

def buat_insight_dari_grafik(data, label_x, label_y, judul, jenis_grafik='line'):
    # Konversi data ke Pandas DataFrame
    df = pd.DataFrame(data)
    
    # Buat plot dari data
    plt.figure(figsize=(10, 6))
    
    if jenis_grafik == 'line':
        plt.plot(df[label_x], df[label_y], marker='o', linestyle='-')
    
    plt.title(judul)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.grid(True)
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
    variabel A dengan "label_x": "{label_x}",
    variabel B dengan "label_y": "{label_y}",
    "judul": "{judul}",
    yang akan menjadi gambaran visualisasi jenis "jenis_grafik": "{jenis_grafik}".
    grafik ini menunjukkan perubahan penjualan dari waktu ke waktu. Analisis harus mencakup:
    - Tren utama yang terlihat dalam data
    - Puncak dan penurunan yang signifikan
    Berikan narasi yang mudah dipahami dan menarik agar dapat dengan mudah dipahami oleh orang yang tidak memiliki latar belakang teknis.
    """
    
    # Definisikan prompt pengguna (instruksi atau pertanyaan spesifik pengguna)
    prompt_pengguna = "Buatlah narasi insight dari data dan visualisasi di atas."

    # Menghasilkan narasi dari AI
    narasi = generate_narrative(sistem_prompt, prompt_pengguna)

    return narasi

# Baca data dari file CSV
data_file = "C:/Users/IYOM/myenvir/sales_by_year_line.csv"
data = pd.read_csv(data_file)

# Konversi data ke format yang sesuai
data_dict = {
    "Order Year": data["Order Year"].tolist(),
    "Sales": data["Sales"].tolist()
}

# Hasilkan insight untuk grafik garis
insight_garis = buat_insight_dari_grafik(data_dict, "Order Year", "Sales", "Penjualan Tahunan", jenis_grafik='line')
print("Insight Grafik Garis:\n", insight_garis)

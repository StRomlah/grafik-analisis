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

def buat_insight_dari_grafik(data, label_x, label_y, judul, jenis_grafik='scatter'):
    # Konversi data ke Pandas DataFrame
    df = pd.DataFrame(data)
    
    # Buat plot dari data
    plt.figure(figsize=(10, 6))
    
    if jenis_grafik == 'scatter':
        plt.scatter(df[label_x], df[label_y])
    
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
    Berikut adalah data yang perlu Anda analisis:
    {data_json}
    
    Grafik ini adalah scatter plot yang menunjukkan hubungan antara "{label_x}" dan "{label_y}" dengan judul "{judul}". Analisis harus mencakup:
    - Korelasi antara kedua variabel
    - Pola atau tren yang terlihat dalam data
    - Poin-poin outlier yang signifikan
    - Rekomendasi berdasarkan temuan
    
    Berikan narasi yang mudah dipahami dan menarik agar dapat dengan mudah dipahami oleh orang yang tidak memiliki latar belakang teknis.
    """
    
    # Definisikan prompt pengguna (instruksi atau pertanyaan spesifik pengguna)
    prompt_pengguna = "Buatlah narasi insight dari data dan visualisasi di atas dengan bahasa yang mudah dipahami."

    # Menghasilkan narasi dari AI
    narasi = generate_narrative(sistem_prompt, prompt_pengguna)

    return narasi

# Baca data dari file CSV
data_file = "C:/Users/IYOM/myenvir/df_scatterr.csv"
data = pd.read_csv(data_file)

# Tampilkan kolom untuk memastikan nama kolom yang benar
print(data.columns)

# Konversi data ke format yang sesuai
data_dict = {
    "Sales": data["Sales"].tolist(),
    "Profit": data["Profit"].tolist()
}

# Hasilkan insight untuk scatter plot
judul_grafik = "Hubungan Antara Variable X dan Variable Y"
insight_scatter = buat_insight_dari_grafik(data_dict, "Sales", "Profit", "Hubungan Sales dengan Profit", jenis_grafik='scatter')
print("Insight Grafik Scatter:\n", insight_scatter)

# Simpan output ke file teks
output_file = os.path.join(os.path.dirname(data_file), "insight_output_scatter.txt")
with open(output_file, "w") as file:
    file.write("Insight Grafik Scatter:\n")
    file.write(insight_scatter)

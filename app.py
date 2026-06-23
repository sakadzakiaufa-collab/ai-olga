from flask import Flask, request, jsonify
from google import genai
import json
import os

app = Flask(__name__)

# ==================== MASUKKAN TOKEN GEMINI KAMU DI SINI ====================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ============================================================================

# Inisialisasi Client Gemini
client = genai.Client(api_key="GEMINI_API_KEY")


# 1. FUNGSI UNTUK MENGHITUNG KALORI (SEKARANG SUDAH PAKAI GEMINI AI)
@app.route('/analyze-food', methods=['POST'])
def analyze_food():
    if 'food_image' not in request.files:
        return jsonify({"nama_makanan": "Error", "estimasi_kalori": "0 Kcal", "saran_kesehatan": "Gambar tidak ditemukan oleh server."}), 400
        
    file = request.files['food_image']
    if file.filename == '':
        return jsonify({"nama_makanan": "Error", "estimasi_kalori": "0 Kcal", "saran_kesehatan": "Nama file kosong."}), 400

    try:
        image_bytes = file.read()
        
        prompt = """
        Analisis gambar makanan ini dengan akurat sebagai ahli gizi profesional.
        Berikan jawaban dalam format JSON mentah (MURNI JSON, tanpa markdown, tanpa ```json ... ```) dengan struktur seperti ini:
        {
          "nama_makanan": "Nama Makanan Yang Terdeteksi",
          "estimasi_kalori": "Total Kalori (misal: 350 Kcal)",
          "makronutrisi": {
            "karbohidrat": "Jumlah dalam gram (misal: 45g)",
            "protein": "Jumlah dalam gram (misal: 12g)",
            "lemak": "Jumlah dalam gram (misal: 10g)"
          },
          "saran_kesehatan": "Berikan saran kesehatan singkat mengenai makanan ini untuk pelaku diet atau fitness."
        }
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                prompt,
                {"inline_data": {"mime_type": file.content_type, "data": image_bytes}}
            ]
        )
        
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(clean_text)
        return jsonify(result_json)
        
    except Exception as e:
        return jsonify({
            "nama_makanan": "Gagal Analisis",
            "estimasi_kalori": "0 Kcal",
            "makronutrisi": {"karbohidrat": "0g", "protein": "0g", "lemak": "0g"},
            "saran_kesehatan": f"Terjadi kesalahan saat memproses gambar dengan Gemini: {str(e)}"
        }), 500


# 2. FUNGSI UNTUK GENERATE WORKOUT PLAN (TETAP AMAN DI SINI)
@app.route('/api/generate-workout', methods=['POST'])
def generate_workout():
    data = request.json
    nama = data.get('nama')
    tinggi = data.get('tinggi')
    berat = data.get('berat')
    frekuensi = data.get('frekuensi')
    tujuan = data.get('tujuan')
    alat = data.get('alat')
    
    prompt = f"""
    Kamu adalah seorang AI Personal Trainer profesional & Ahli Gizi Kesehatan bernama Arise Coach.
    Buatkan rencana latihan (workout plan) khusus yang personal dan detail berdasarkan data klien berikut:
    
    - Nama Klien: {nama}
    - Tinggi Badan: {tinggi} cm
    - Berat Badan: {berat} kg
    - Frekuensi Olahraga ideal: {frekuensi}
    - Target / Goal: {tujuan}
    - Ketersediaan Alat di Rumah: {alat}
    
    Berikan respon yang memotivasi, gunakan bahasa Indonesia yang santai tapi profesional, 
    serta berikan contoh gerakan konkret yang bisa langsung mereka praktikkan sesuai ketersediaan alatnya!
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({"rencana_latihan": response.text})
    except Exception as e:
        return jsonify({"rencana_latihan": f"Aduh, gagal nanya ke Gemini AI nih. Detail error: {str(e)}"}), 500


# 3. FUNGSI UNTUK CHAT AI COACH
@app.route('/api/chat', methods=['POST'])
def chat_ai():
    data = request.json
    user_message = data.get('message')
    
    prompt = f"""
    Kamu adalah Arise Personal AI Coach, asisten kesehatan pintar. 
    Jawab pertanyaan user berikut tentang fitness, diet, atau kalori dengan ramah dan solutif.
    Pertanyaan: "{user_message}"
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Gagal memproses obrolan. Error: {str(e)}"}), 500


# BLOK RUNNING UTAMA (WAJIB PALING BAWAH)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
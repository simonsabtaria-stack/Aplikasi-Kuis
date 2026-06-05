import streamlit as st
import pandas as pd
import io
import json # Tambahan untuk membaca data dari AI
import google.generativeai as genai # Tambahan untuk memanggil Koki AI
from supabase import create_client, Client

# --- MENGHUBUNGKAN KE SUPABASE & GEMINI ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    # Mengaktifkan Koki AI Gemini
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    st.error("Gagal terhubung. Pastikan SUPABASE_URL, SUPABASE_KEY, dan GEMINI_API_KEY ada di Secrets Streamlit.")

# --- NAVIGASI UTAMA (SIDEBAR) ---
st.sidebar.title("🕊️ Menu Aplikasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Mulai Kuis (Siswa)", "Dashboard Rekap (Guru)", "Dapur AI (Buat Soal)"])

# ==============================================================================
# HALAMAN 1: KUIS SISWA
# ==============================================================================
if menu == "Mulai Kuis (Siswa)":
    st.title("Kuis Formatif Agama Katolik ✝️")
    st.write("Jawablah pertanyaan di bawah ini dengan memilih opsi yang paling tepat.")
    st.divider()

    st.subheader("📝 Isi Identitas Diri")
    nama_siswa = st.text_input("Nama Lengkap (Wajib diisi):")
    kelas_siswa = st.selectbox("Kelas:", ["Pilih Kelas", "Fase D - Kelas 7", "Fase D - Kelas 8", "Fase D - Kelas 9"])
    st.divider()

    try:
        respon_soal = supabase.table("bank_soal").select("*").execute()
        data_soal = respon_soal.data

        if not data_soal:
            st.info("📭 Kulkas soal masih kosong! Guru belum membuat soal di Dapur AI.")
        else:
            # Menyaring soal agar hanya memunculkan soal sesuai kelas yang dipilih siswa
            df = pd.DataFrame(data_soal)
            if kelas_siswa != "Pilih Kelas":
                df = df[df['fase_kelas'] == kelas_siswa].reset_index(drop=True)
            
            if df.empty and kelas_siswa != "Pilih Kelas":
                st.warning(f"Belum ada soal untuk kelas {kelas_siswa}.")
            elif kelas_siswa != "Pilih Kelas":
                jawaban_user = {}

                for index, baris in df.iterrows():
                    nomor_soal = index + 1
                    st.write(f"**{nomor_soal}. {baris['pertanyaan']}**")
                    
                    pilihan_tampil = (
                        f"A. {baris['opsi_a']}",
                        f"B. {baris['opsi_b']}",
                        f"C. {baris['opsi_c']}",
                        f"D. {baris['opsi_d']}"
                    )
                    
                    jawaban = st.radio("Pilih jawaban:", pilihan_tampil, index=None, key=f"soal_{index}", label_visibility="collapsed")
                    jawaban_user[index] = jawaban
                    st.write("") 
                    
                st.divider()

                if st.button("Kirim Jawaban"):
                    if nama_siswa == "":
                        st.warning("⚠️ Tunggu dulu! Mohon isi Nama Lengkap Anda.")
                    else:
                        benar = 0
                        for index, baris in df.iterrows():
                            pilihan_siswa = jawaban_user[index][0] if jawaban_user[index] else ""
                            if pilihan_siswa == baris['jawaban_benar']:
                                benar += 1
                        
                        total_soal = len(df)
                        nilai_akhir = int((benar / total_soal) * 100)
                        
                        if nilai_akhir == 100:
                            st.success(f"Luar biasa, {nama_siswa}! Nilai Anda Sempurna: {nilai_akhir}")
                            st.balloons() 
                        elif nilai_akhir >= 50:
                            st.warning(f"Cukup baik, {nama_siswa}. Nilai Anda: {nilai_akhir}. Terus semangat!")
                        else:
                            st.error(f"Nilai Anda: {nilai_akhir}. Jangan menyerah, {nama_siswa}, perbanyak latihan!")
                        
                        try:
                            data_dikirim = {
                                "nama_siswa": nama_siswa,
                                "kelas": kelas_siswa,
                                "nilai_akhir": nilai_akhir
                            }
                            supabase.table("nilai_kuis").insert(data_dikirim).execute()
                            st.success("✅ Nilai Anda telah berhasil direkam oleh sistem!")
                        except Exception as e:
                            st.error(f"❌ Gagal mengirim nilai ke database: {e}")
                
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menarik soal: {e}")

# ==============================================================================
# HALAMAN 2: DASHBOARD GURU
# ==============================================================================
elif menu == "Dashboard Rekap (Guru)":
    st.title("🛡️ Pintu Belakang: Rekap Nilai Siswa")
    st.divider()

    password_input = st.text_input("Masukkan Kata Sandi Guru:", type="password")
    PASSWORD_RAHASIA = "guruamoris" 

    if password_input == PASSWORD_RAHASIA:
        st.success("🔓 Akses diterima! Memuat data...")
        try:
            respon = supabase.table("nilai_kuis").select("created_at, nama_siswa, kelas, nilai_akhir").order("created_at", desc=True).execute()
            if respon.data:
                df_nilai = pd.DataFrame(respon.data)
                df_nilai.columns = ["Waktu Pengerjaan", "Nama Siswa", "Kelas", "Nilai Akhir"]
                st.dataframe(df_nilai, use_container_width=True)
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_nilai.to_excel(writer, index=False, sheet_name='Rekap Nilai')
                
                st.download_button("📊 Unduh Rekap Nilai (Excel)", data=buffer.getvalue(), file_name="Rekap_Nilai.xlsx")
            else:
                st.info("Belum ada data nilai.")
        except Exception as e:
            st.error(f"Gagal menarik data: {e}")
    elif password_input != "":
        st.error("🔒 Kata sandi salah!")

# ==============================================================================
# HALAMAN 3: DAPUR AI (BUAT SOAL)
# ==============================================================================
elif menu == "Dapur AI (Buat Soal)":
    st.title("👨‍🍳 Dapur Koki AI: Pembuat Soal")
    st.write("Masukkan materi, dan AI akan otomatis meracik soal untuk siswa.")
    st.divider()

    password_input = st.text_input("Masukkan Kata Sandi Guru:", type="password", key="pass_dapur")
    PASSWORD_RAHASIA = "guruamoris" 

    if password_input == PASSWORD_RAHASIA:
        st.success("🔓 Akses dapur AI terbuka!")
        
        fase_kelas = st.selectbox("Target Kelas:", ["Fase D - Kelas 7", "Fase D - Kelas 8", "Fase D - Kelas 9"])
        topik = st.text_input("Topik/Materi Pelajaran:", placeholder="Contoh: Manusia Sebagai Citra Allah")
        jumlah_soal = st.number_input("Jumlah Soal yang Ingin Dibuat:", min_value=1, max_value=10, value=3)
        
        if st.button("🪄 Buat Soal dengan AI"):
            if topik == "":
                st.warning("Mohon isi topik materi terlebih dahulu.")
            else:
                with st.spinner("Koki AI sedang memikirkan soal... Mohon tunggu sekitar 15 detik."):
                    try:
                        # Memberi instruksi (Prompt) ke Gemini AI
                        prompt = f"""
                        Buatlah {jumlah_soal} soal pilihan ganda mata pelajaran Agama Katolik untuk {fase_kelas} dengan topik "{topik}".
                        Berikan hasilnya HANYA dalam format JSON array yang valid, tanpa teks awalan atau akhiran.
                        Struktur setiap soal dalam JSON wajib seperti ini:
                        [
                          {{
                            "pertanyaan": "Teks pertanyaan di sini",
                            "opsi_a": "Teks opsi A",
                            "opsi_b": "Teks opsi B",
                            "opsi_c": "Teks opsi C",
                            "opsi_d": "Teks opsi D",
                            "jawaban_benar": "A"
                          }}
                        ]
                        Penting: Kolom jawaban_benar hanya boleh diisi huruf kapital A, B, C, atau D.
                        """
                        
                        # Memanggil Gemini AI
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt)
                        
                        # Membersihkan teks agar menjadi JSON murni
                        teks_json = response.text.strip()
                        if teks_json.startswith("```json"):
                            teks_json = teks_json[7:]
                        if teks_json.endswith("```"):
                            teks_json = teks_json[:-3]
                            
                        # Menerjemahkan JSON ke dalam data Python
                        data_ai = json.loads(teks_json)
                        
                        # Menyimpan satu per satu soal ke brankas Supabase
                        for soal in data_ai:
                            data_simpan = {
                                "fase_kelas": fase_kelas,
                                "topik": topik,
                                "pertanyaan": soal["pertanyaan"],
                                "opsi_a": soal["opsi_a"],
                                "opsi_b": soal["opsi_b"],
                                "opsi_c": soal["opsi_c"],
                                "opsi_d": soal["opsi_d"],
                                "jawaban_benar": soal["jawaban_benar"]
                            }
                            supabase.table("bank_soal").insert(data_simpan).execute()
                            
                        st.success(f"✅ BINGO! {jumlah_soal} soal baru berhasil dibuat dan disimpan ke Bank Soal!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan saat AI membuat soal: {e}")
                        st.info("Saran: Coba klik tombol 'Buat Soal' sekali lagi. Kadang Koki AI butuh waktu.")

    elif password_input != "":
        st.error("🔒 Kata sandi salah!")

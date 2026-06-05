import streamlit as st
import pandas as pd
from supabase import create_client, Client # TAMBAHAN BARU

# --- MENGHUBUNGKAN KE SUPABASE ---
try:
    # Memanggil kunci rahasia dari secrets.toml
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Gagal terhubung ke Supabase. Cek file secrets.toml Anda.")
# ---------------------------------

st.set_page_config(page_title="Kuis Agama Katolik", page_icon="🕊️")

st.title("Kuis Formatif: Manusia Sebagai Citra Allah ✝️")
st.write("Jawablah pertanyaan di bawah ini dengan memilih opsi yang paling tepat.")
st.divider()

st.subheader("📝 Isi Identitas Diri")
nama_siswa = st.text_input("Nama Lengkap (Wajib diisi):")
kelas_siswa = st.selectbox("Kelas:", ["Pilih Kelas", "Fase D - Kelas 7", "Fase D - Kelas 8", "Fase D - Kelas 9"])
st.divider()

try:
    df = pd.read_excel("Soal_Kuis.xlsx")
    jawaban_user = {}

    for index, baris in df.iterrows():
        st.write(f"**{baris['No']}. {baris['Pertanyaan']}**")
        pilihan = (baris['Opsi A'], baris['Opsi B'], baris['Opsi C'], baris['Opsi D'])
        jawaban = st.radio("Pilih jawaban:", pilihan, index=None, key=f"soal_{index}", label_visibility="collapsed")
        jawaban_user[index] = jawaban
        st.write("") 
        
    st.divider()

    if st.button("Kirim Jawaban"):
        if nama_siswa == "" or kelas_siswa == "Pilih Kelas":
            st.warning("⚠️ Tunggu dulu! Mohon isi Nama Lengkap dan Kelas Anda di bagian atas sebelum mengirim jawaban.")
        else:
            benar = 0
            for index, baris in df.iterrows():
                if jawaban_user[index] == baris['Jawaban Benar']:
                    benar += 1
            
            total_soal = len(df)
            nilai_akhir = int((benar / total_soal) * 100)
            
            if nilai_akhir == 100:
                st.success(f"Luar biasa, {nama_siswa}! Nilai Anda Sempurna: {nilai_akhir}")
                st.balloons() 
            elif nilai_akhir >= 50:
                st.warning(f"Cukup baik, {nama_siswa}. Nilai Anda: {nilai_akhir}. Terus semangat belajar!")
            else:
                st.error(f"Nilai Anda: {nilai_akhir}. Jangan menyerah, {nama_siswa}, mari perbanyak latihan!")
            
            # --- BAGIAN BARU: MENGIRIM DATA KE SUPABASE ---
            try:
                data_dikirim = {
                    "nama_siswa": nama_siswa,
                    "kelas": kelas_siswa,
                    "nilai_akhir": nilai_akhir
                }
                # Menyisipkan data ke tabel 'nilai_kuis'
                proses_kirim = supabase.table("nilai_kuis").insert(data_dikirim).execute()
                st.success("✅ Nilai Anda telah berhasil direkam oleh sistem!")
            except Exception as e:
                st.error(f"❌ Gagal mengirim nilai ke database: {e}")
            # ----------------------------------------------
            
except FileNotFoundError:
    st.error("⚠️ File 'Soal_Kuis.xlsx' tidak ditemukan! Pastikan file berada di folder yang sama.")
except Exception as e:
    st.error(f"Terjadi kesalahan pada aplikasi: {e}")

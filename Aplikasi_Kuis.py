import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kuis Agama Katolik", page_icon="🕊️")

st.title("Kuis Formatif✝️")
st.write("Jawablah pertanyaan di bawah ini dengan memilih opsi yang paling tepat.")
st.divider()

# --- BAGIAN BARU: BUKU TAMU (IDENTITAS SISWA) ---
st.subheader("📝 Isi Identitas Diri")
nama_siswa = st.text_input("Nama Lengkap (Wajib diisi):")
# Anda bisa mengubah daftar kelas ini sesuai dengan yang Anda ajar
kelas_siswa = st.selectbox("Kelas:", ["Pilih Kelas", "Fase D - Kelas 7", "Fase D - Kelas 8", "Fase D - Kelas 9"])
st.divider()
# ------------------------------------------------

try:
    df = pd.read_excel("Soal_Kuis.xlsx")
    jawaban_user = {}

    # Membaca dan menampilkan soal dari Excel
    for index, baris in df.iterrows():
        st.write(f"**{baris['No']}. {baris['Pertanyaan']}**")
        pilihan = (baris['Opsi A'], baris['Opsi B'], baris['Opsi C'], baris['Opsi D'])
        jawaban = st.radio("Pilih jawaban:", pilihan, index=None, key=f"soal_{index}", label_visibility="collapsed")
        jawaban_user[index] = jawaban
        st.write("") 
        
    st.divider()

    if st.button("Kirim Jawaban"):
        # VALIDASI: Cek apakah nama dan kelas sudah diisi
        if nama_siswa == "" or kelas_siswa == "Pilih Kelas":
            st.warning("⚠️ Tunggu dulu! Mohon isi Nama Lengkap dan Kelas Anda di bagian atas sebelum mengirim jawaban.")
        else:
            # Mesin penghitung nilai berjalan
            benar = 0
            for index, baris in df.iterrows():
                if jawaban_user[index] == baris['Jawaban Benar']:
                    benar += 1
            
            total_soal = len(df)
            nilai_akhir = int((benar / total_soal) * 100)
            
            # Tampilkan hasil secara personal dengan menyebut nama siswa
            if nilai_akhir == 100:
                st.success(f"Luar biasa, {nama_siswa}! Nilai Anda Sempurna: {nilai_akhir}")
                st.balloons() 
            elif nilai_akhir >= 50:
                st.warning(f"Cukup baik, {nama_siswa}. Nilai Anda: {nilai_akhir}. Terus semangat belajar!")
            else:
                st.error(f"Nilai Anda: {nilai_akhir}. Jangan menyerah, {nama_siswa}, mari perbanyak latihan!")
            
            # --- AREA PERSIAPAN DATABASE ---
            # Pesan ini hanya simulasi untuk menunjukkan data siap dikirim
            st.info(f"💾 Simulasi Sistem: Data atas nama **{nama_siswa}** ({kelas_siswa}) dengan nilai **{nilai_akhir}** siap disetorkan ke brankas Supabase!")
            
except FileNotFoundError:
    st.error("⚠️ File 'Soal_Kuis.xlsx' tidak ditemukan! Pastikan file berada di folder yang sama.")
except Exception as e:
    st.error(f"Terjadi kesalahan pada aplikasi: {e}")

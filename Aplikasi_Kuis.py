import streamlit as st
import pandas as pd
import io  # Tambahan untuk memproses unduhan Excel
from supabase import create_client, Client

# --- MENGHUBUNGKAN KE SUPABASE ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Gagal terhubung ke Supabase. Cek file secrets.toml atau Settings di Streamlit Cloud.")

# --- NAVIGASI UTAMA (SIDEBAR) ---
st.sidebar.title("🕊️ Menu Aplikasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Mulai Kuis (Siswa)", "Dashboard Rekap (Guru)"])

# ==============================================================================
# HALAMAN 1: KUIS SISWA
# ==============================================================================
if menu == "Mulai Kuis (Siswa)":
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
                
                # Mengirim data ke Supabase
    try:
        # --- PIPA BARU: MENYEDOT SOAL DARI SUPABASE ---
        respon_soal = supabase.table("bank_soal").select("*").execute()
        data_soal = respon_soal.data

        if not data_soal:
            st.info("📭 Kulkas soal masih kosong! Belum ada soal di dalam Bank Soal.")
        else:
            df = pd.DataFrame(data_soal)
            jawaban_user = {}

            # Mencetak soal dari database ke layar
            for index, baris in df.iterrows():
                nomor_soal = index + 1
                st.write(f"**{nomor_soal}. {baris['pertanyaan']}**")
                
                # Menggabungkan huruf A, B, C, D dengan teks opsi
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
                if nama_siswa == "" or kelas_siswa == "Pilih Kelas":
                    st.warning("⚠️ Tunggu dulu! Mohon isi Nama Lengkap dan Kelas Anda di bagian atas sebelum mengirim jawaban.")
                else:
                    benar = 0
                    for index, baris in df.iterrows():
                        # TRIK CERDAS: Kita hanya mengambil huruf pertama (A/B/C/D) dari jawaban siswa
                        # Jika siswa memilih "C. Memiliki akal budi...", kita ambil huruf "C" saja
                        # Lalu dicocokkan dengan kolom jawaban_benar di database
                        pilihan_siswa = jawaban_user[index][0] if jawaban_user[index] else ""
                        if pilihan_siswa == baris['jawaban_benar']:
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
                    
                    # Mengirim data ke Supabase (TIDAK ADA YANG BERUBAH DI SINI)
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
# HALAMAN 2: DASHBOARD GURU (PINTU BELAKANG)
# ==============================================================================
elif menu == "Dashboard Rekap (Guru)":
    st.title("🛡️ Pintu Belakang Dapur: Rekap Nilai Siswa")
    st.write("Halaman ini khusus untuk Guru melihat dan mengunduh hasil kuis siswa.")
    st.divider()

    # Sistem Proteksi Password Sederhana
    password_input = st.text_input("Masukkan Kata Sandi Guru:", type="password")
    
    # SILAKAN UBAH PASSWORD DI BAWAH INI SESUAI KEINGINAN ANDA
    PASSWORD_RAHASIA = "guruamoris" 

    if password_input == PASSWORD_RAHASIA:
        st.success("🔓 Akses diterima! Memuat data dari brankas Supabase...")
        
        try:
            # Mengambil seluruh data nilai dari tabel 'nilai_kuis'
            respon = supabase.table("nilai_kuis").select("created_at, nama_siswa, kelas, nilai_akhir").order("created_at", desc=True).execute()
            data_nilai = respon.data

            if data_nilai:
                # Mengubah data dari Supabase menjadi Tabel Pandas (DataFrame)
                df_nilai = pd.DataFrame(data_nilai)
                
                # Mempercantik nama kolom tabel saat ditampilkan
                df_nilai.columns = ["Waktu Pengerjaan", "Nama Siswa", "Kelas", "Nilai Akhir"]
                
                # Menampilkan total peserta kuis saat ini
                st.metric(label="Total Siswa Sudah Mengerjakan", value=len(df_nilai))
                
                # Menampilkan tabel data di layar Streamlit
                st.dataframe(df_nilai, use_container_width=True)
                
                st.divider()
                st.subheader("📥 Ekspor Data Nilai")
                
                # LOGIKA PROSES UNDUH KE EXCEL (Konversi data ke file Excel langsung di memori)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_nilai.to_excel(writer, index=False, sheet_name='Rekap Nilai')
                
                # Menampilkan Tombol Unduh Excel
                st.download_button(
                    label="📊 Unduh Rekap Nilai (Format Excel .xlsx)",
                    data=buffer.getvalue(),
                    file_name="Rekap_Nilai_Kuis_Katolik.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            else:
                st.info("Kulkas kosong! Belum ada siswa yang mengirimkan jawaban hari ini.")
                
        except Exception as e:
            st.error(f"Gagal menarik data dari Supabase: {e}")
            
    elif password_input != "" and password_input != PASSWORD_RAHASIA:
        st.error("🔒 Kata sandi salah! Akses ke dapur ditolak.")

import streamlit as st
import pandas as pd


st.set_page_config(page_title="Kuis Fisika", page_icon="⚛️")
st.title("Kuis Formatif: Energi & Kecepatan 🚀")
st.write("Jawablah pertanyaan di bawah ini dengan memilih opsi yang paling tepat.")
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
        benar = 0
        
        
        for index, baris in df.iterrows():
            if jawaban_user[index] == baris['Jawaban Benar']:
                benar += 1
        
        
        total_soal = len(df)
        nilai_akhir = int((benar / total_soal) * 100)
        
        
        if nilai_akhir == 100:
            st.success(f"Luar biasa! Nilai Anda Sempurna: {nilai_akhir}")
            st.balloons() 
        elif nilai_akhir >= 50:
            st.warning(f"Cukup baik. Nilai Anda: {nilai_akhir}. Terus semangat belajar!")
        else:
            st.error(f"Nilai Anda: {nilai_akhir}. Jangan menyerah, mari perbanyak latihan!")
            
except FileNotFoundError:
    st.error("⚠️ File 'Soal_Kuis.xlsx' tidak ditemukan! Pastikan Anda sudah membuat file Excel-nya dan menyimpannya di folder yang sama.")
except Exception as e:
    st.error(f"Terjadi kesalahan pada data Excel Anda: {e}")

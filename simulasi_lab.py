import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import random

# Konfigurasi halaman
st.set_page_config(
    page_title="Simulasi Laboratorium Kimia",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi state
if 'campuran' not in st.session_state:
    st.session_state.campuran = []
if 'reaksi' not in st.session_state:
    st.session_state.reaksi = ""
if 'warna' not in st.session_state:
    st.session_state.warna = "#FFFFFF"
if 'suhu' not in st.session_state:
    st.session_state.suhu = 25
if 'gambar_reaksi' not in st.session_state:
    st.session_state.gambar_reaksi = None
if 'log_percobaan' not in st.session_state:
    st.session_state.log_percobaan = []

# Database zat kimia
ZAT_KIMIA = {
    "Asam Klorida (HCl)": {
        "warna": "#FFFFFF",
        "reaksi": {
            "Natrium Hidroksida (NaOH)": "Netralisasi: menghasilkan NaCl dan air",
            "Tembaga Sulfat (CuSO4)": "Tidak bereaksi",
            "Besi (Fe)": "Menghasilkan gas hidrogen dan besi klorida",
            "Fenolftalein": "Tetap tak berwarna"
        },
        "jenis": "asam"
    },
    "Natrium Hidroksida (NaOH)": {
        "warna": "#FFFFFF",
        "reaksi": {
            "Asam Klorida (HCl)": "Netralisasi: menghasilkan NaCl dan air",
            "Tembaga Sulfat (CuSO4)": "Menghasilkan endapan biru Cu(OH)₂",
            "Besi (Fe)": "Tidak bereaksi",
            "Fenolftalein": "Berubah menjadi merah muda"
        },
        "jenis": "basa"
    },
    "Tembaga Sulfat (CuSO4)": {
        "warna": "#00B4D8",
        "reaksi": {
            "Asam Klorida (HCl)": "Tidak bereaksi",
            "Natrium Hidroksida (NaOH)": "Menghasilkan endapan biru Cu(OH)₂",
            "Besi (Fe)": "Reaksi pengendapan tembaga",
            "Fenolftalein": "Tidak bereaksi"
        },
        "jenis": "garam"
    },
    "Besi (Fe)": {
        "warna": "#B5651D",
        "reaksi": {
            "Asam Klorida (HCl)": "Menghasilkan gas hidrogen dan besi klorida",
            "Natrium Hidroksida (NaOH)": "Tidak bereaksi",
            "Tembaga Sulfat (CuSO4)": "Reaksi pengendapan tembaga",
            "Fenolftalein": "Tidak bereaksi"
        },
        "jenis": "logam"
    },
    "Fenolftalein": {
        "warna": "#FFFFFF",
        "reaksi": {
            "Asam Klorida (HCl)": "Tetap tak berwarna",
            "Natrium Hidroksida (NaOH)": "Berubah menjadi merah muda",
            "Tembaga Sulfat (CuSO4)": "Tidak bereaksi",
            "Besi (Fe)": "Tidak bereaksi"
        },
        "jenis": "indikator"
    },
    "Air (H2O)": {
        "warna": "#ADD8E6",
        "reaksi": {
            "Asam Klorida (HCl)": "Pengenceran asam",
            "Natrium Hidroksida (NaOH)": "Pengenceran basa",
            "Tembaga Sulfat (CuSO4)": "Larutan berwarna biru",
            "Besi (Fe)": "Korosi lambat"
        },
        "jenis": "pelarut"
    }
}

# Fungsi untuk mencampur warna
def campur_warna(warna1, warna2):
    def hex_to_rgb(hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % tuple(min(255, max(0, int(c))) for c in rgb)
    
    rgb1 = hex_to_rgb(warna1)
    rgb2 = hex_to_rgb(warna2)
    
    # Campur warna dengan rata-rata tertimbang
    total_volume = volume1 + volume2
    campuran = [
        int((c1 * volume1 + c2 * volume2) / total_volume)
        for c1, c2 in zip(rgb1, rgb2)
    ]
    
    return rgb_to_hex(campuran)

# Fungsi untuk mendapatkan reaksi
def dapatkan_reaksi(zat1, zat2, suhu):
    # Cek reaksi langsung
    if zat2 in ZAT_KIMIA[zat1]["reaksi"]:
        return ZAT_KIMIA[zat1]["reaksi"][zat2]
    
    # Cek reaksi terbalik
    if zat1 in ZAT_KIMIA[zat2]["reaksi"]:
        return ZAT_KIMIA[zat2]["reaksi"][zat1]
    
    # Reaksi generik berdasarkan jenis zat
    jenis1 = ZAT_KIMIA[zat1]["jenis"]
    jenis2 = ZAT_KIMIA[zat2]["jenis"]
    
    if jenis1 == "asam" and jenis2 == "basa":
        return "Reaksi netralisasi: menghasilkan garam dan air"
    elif jenis1 == "logam" and jenis2 == "asam":
        return "Reaksi logam dengan asam: menghasilkan garam dan gas hidrogen"
    elif "indikator" in [jenis1, jenis2]:
        return "Perubahan warna indikator"
    
    # Reaksi berdasarkan suhu
    if suhu > 50:
        return f"Reaksi dekomposisi pada suhu tinggi ({suhu}°C)"
    elif suhu < 10:
        return "Reaksi melambat karena suhu rendah"
    
    return "Tidak ada reaksi yang teramati"

# Fungsi buat gambar reaksi
def buat_gambar_reaksi(warna, teks_reaksi):
    img = Image.new('RGB', (400, 300), color=warna)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Gambar labu
    draw.ellipse([(100, 50), (300, 250)], outline="black", width=3)
    draw.rectangle([(190, 20), (210, 50)], fill="gray")
    
    # Tambahkan teks reaksi
    lines = []
    current_line = ""
    for word in teks_reaksi.split():
        if len(current_line + word) < 30:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    if current_line:
        lines.append(current_line)
    
    y_text = 260
    for line in lines:
        draw.text((50, y_text), line, fill="black", font=font)
        y_text += 20
    
    return img

# ===== UI APLIKASI =====
st.title("🧪 Simulasi Laboratorium Kimia")
st.markdown("""
*Aplikasi ini mensimulasikan percampuran zat kimia di laboratorium.*
Tambahkan zat ke dalam labu, atur suhu, dan lihat reaksi yang terjadi!
""")

# Sidebar untuk input
with st.sidebar:
    st.header("⚗ Kontrol Percobaan")
    zat = st.selectbox("Pilih Zat Kimia", list(ZAT_KIMIA.keys()))
    volume = st.slider("Volume (mL)", 1, 100, 30)
    suhu = st.slider("Suhu (°C)", -10, 100, 25)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Tambahkan ke Labu", use_container_width=True):
            st.session_state.campuran.append({
                "zat": zat,
                "volume": volume,
                "warna": ZAT_KIMIA[zat]["warna"]
            })
            st.session_state.suhu = suhu
            st.success(f"{volume}mL {zat} ditambahkan!")
            
    with col2:
        if st.button("🧼 Bersihkan Labu", use_container_width=True, type="primary"):
            st.session_state.campuran = []
            st.session_state.reaksi = ""
            st.session_state.warna = "#FFFFFF"
            st.session_state.gambar_reaksi = None
            st.session_state.log_percobaan.append("Labu dibersihkan")
            st.success("Labu siap untuk percobaan baru!")

# Tampilan utama
tab1, tab2, tab3 = st.tabs(["Lab Percobaan", "Log Eksperimen", "Panduan"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🧫 Labu Percobaan")
        
        if st.session_state.campuran:
            # Hitung warna campuran
            current_color = st.session_state.campuran[0]["warna"]
            total_volume = st.session_state.campuran[0]["volume"]
            
            for i in range(1, len(st.session_state.campuran)):
                next_color = st.session_state.campuran[i]["warna"]
                next_volume = st.session_state.campuran[i]["volume"]
                current_color = campur_warna(
                    current_color, 
                    next_color,
                    total_volume,
                    next_volume
                )
                total_volume += next_volume
            
            st.session_state.warna = current_color
            
            # Tampilkan labu dengan warna campuran
            labu_html = f"""
            <div style="
                width: 200px;
                height: 300px;
                background-color: {current_color};
                border-radius: 50% 50% 10% 10% / 60% 60% 10% 10%;
                margin: 0 auto;
                border: 3px solid #333;
                position: relative;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <div style="
                    width: 30px;
                    height: 50px;
                    background: #ddd;
                    position: absolute;
                    top: -50px;
                    left: 85px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                "></div>
            </div>
            """
            st.markdown(labu_html, unsafe_allow_html=True)
            
            # Tampilkan informasi campuran
            st.write(f"*Suhu:* {st.session_state.suhu}°C")
            st.write(f"*Volume Total:* {total_volume}mL")
            st.color_picker("Warna Campuran", current_color, disabled=True)
            
            # Tampilkan daftar zat
            st.write("*Komposisi:*")
            for i, zat in enumerate(st.session_state.campuran, 1):
                st.write(f"{i}. {zat['zat']} ({zat['volume']}mL)")
            
            # Tombol reaksi
            if len(st.session_state.campuran) >= 2:
                if st.button("🔥 Mulai Reaksi!", type="primary", use_container_width=True):
                    zat1 = st.session_state.campuran[0]["zat"]
                    zat2 = st.session_state.campuran[1]["zat"]
                    reaksi = dapatkan_reaksi(
                        zat1, 
                        zat2, 
                        st.session_state.suhu
                    )
                    st.session_state.reaksi = reaksi
                    st.session_state.gambar_reaksi = buat_gambar_reaksi(
                        current_color, 
                        reaksi
                    )
                    log = f"Reaksi: {zat1} + {zat2} → {reaksi}"
                    st.session_state.log_percobaan.append(log)
        else:
            st.info("Labu kosong. Tambahkan zat kimia dari panel kontrol di samping.")
            st.image("https://i.imgur.com/3Jm7F2i.png", caption="Labu kosong", use_column_width=True)

    with col2:
        st.subheader("📊 Hasil Reaksi")
        
        if st.session_state.reaksi:
            st.success(f"*Reaksi Terjadi!*")
            st.info(f"{st.session_state.reaksi}")
            
            if st.session_state.gambar_reaksi:
                img_bytes = io.BytesIO()
                st.session_state.gambar_reaksi.save(img_bytes, format="PNG")
                st.image(img_bytes, caption="Visualisasi Reaksi", use_column_width=True)
            
            # Penjelasan reaksi
            st.subheader("🔍 Penjelasan Ilmiah")
            if "netralisasi" in st.session_state.reaksi.lower():
                st.markdown("""
                *Reaksi Netralisasi:*
                - Terjadi antara asam dan basa
                - Menghasilkan garam dan air
                - Persamaan umum: Asam + Basa → Garam + Air
                """)
            elif "hidrogen" in st.session_state.reaksi.lower():
                st.markdown("""
                *Reaksi Logam dengan Asam:*
                - Logam bereaksi dengan asam menghasilkan garam dan gas hidrogen
                - Persamaan umum: Logam + Asam → Garam + H₂(g)
                - Gas hidrogen mudah terbakar
                """)
            elif "endapan" in st.session_state.reaksi.lower():
                st.markdown("""
                *Reaksi Pengendapan:*
                - Terjadi ketika dua larutan bereaksi membentuk padatan tak larut
                - Endapan biasanya berwarna dan dapat disaring
                """)
        else:
            st.info("Belum ada reaksi. Tambahkan minimal 2 zat dan klik 'Mulai Reaksi'.")
            st.image("https://i.imgur.com/5Z3QY7c.png", caption="Menunggu reaksi", use_column_width=True)

with tab2:
    st.subheader("📝 Log Percobaan")
    
    if st.session_state.log_percobaan:
        st.write("*Riwayat Percobaan:*")
        for i, log in enumerate(st.session_state.log_percobaan, 1):
            st.code(f"{i}. {log}")
        
        if st.button("🧹 Bersihkan Log", type="secondary"):
            st.session_state.log_percobaan = []
            st.success("Log percobaan telah dibersihkan!")
    else:
        st.info("Belum ada catatan percobaan. Lakukan beberapa reaksi untuk mencatatnya.")

with tab3:
    st.subheader("📚 Panduan Penggunaan")
    st.markdown("""
    ### Cara Menggunakan Aplikasi Simulasi Lab Kimia:
    1. *Pilih zat kimia* dari dropdown di panel kiri
    2. *Atur volume* dengan slider (1-100mL)
    3. *Atur suhu* percobaan (-10°C hingga 100°C)
    4. Klik *"Tambahkan ke Labu"* untuk menambahkan zat
    5. Tambahkan *minimal 2 zat* berbeda
    6. Klik *"Mulai Reaksi"* untuk melihat hasil
    7. *Bersihkan labu* untuk memulai percobaan baru
    
    ### Zat Kimia yang Tersedia:
    - *Asam Klorida (HCl)*: Asam kuat
    - *Natrium Hidroksida (NaOH)*: Basa kuat
    - *Tembaga Sulfat (CuSO4)*: Garam berwarna biru
    - *Besi (Fe)*: Logam reaktif
    - *Fenolftalein*: Indikator pH
    - *Air (H2O)*: Pelarut universal
    
    ### Reaksi yang Dapat Disimulasikan:
    - Netralisasi asam-basa
    - Reaksi logam dengan asam
    - Pembentukan endapan
    - Perubahan warna indikator
    - Pengaruh suhu terhadap reaksi
    """)
    
    st.subheader("⚠ Keselamatan Laboratorium")
    st.markdown("""
    - Selalu gunakan jas lab dan pelindung mata
    - Jangan mencium zat kimia secara langsung
    - Hindari kontak langsung dengan kulit
    - Bekerja di ruang dengan ventilasi baik
    - Ketahui lokasi alat keselamatan (pemadam, eye wash)
    """)

# Footer
st.divider()
st.caption("© 2023 Simulasi Laboratorium Kimia | Dibuat dengan Streamlit")

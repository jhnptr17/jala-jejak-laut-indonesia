# JALA — Jejak Laut Indonesia

Dashboard produksi dan ekspor perikanan tangkap Indonesia.

UAS Visualisasi Data dan Informasi — Politeknik Statistika STIS.
Topik: **Multivariat** (38 provinsi) + **Geospasial** (514 kab/kota, choropleth
rasio + proportional symbol absolut) + **Aliran** (Sankey 3-lapis provinsi→Indonesia→negara,
flow map geografis, dan tren garis 2012-2025).

## Fitur desain
- Scroll-reveal: teks & kartu insight muncul fade-in saat discroll (butuh
  koneksi internet untuk Google Fonts; tanpa internet tetap jalan, cuma font
  fallback-nya yang dipakai).
- Latar gradasi kedalaman laut saat scroll, narasi kiri/kanan bergantian, siluet kapal dan ikan (SVG inline).
- Choropleth memakai rasio (harga rata-rata Rp/kg dan % produksi laut) dengan kelas diskret; proportional symbol tetap memakai angka absolut.
- Logo: taruh `assets/logo_bps.png` dan `assets/logo_kkp.png` (logo resmi) agar tampil di bar Sumber Data.
- Flow map datar (Plotly scattergeo, proyeksi Natural Earth) menggantikan globe 3D.
- Halaman mengalir (tanpa tab); bagian Kesimpulan di akhir.
- Tab navigasi pakai `st.iframe` (API baru Streamlit) dengan fallback
  otomatis ke `components.html` kalau versi Streamlit di komputermu lebih
  lama dan belum punya `st.iframe` — jadi aman dipakai di versi lama maupun
  baru tanpa perlu ubah kode.

## Cara menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Struktur proyek
```
app.py                               # aplikasi utama (3 babak/tab + storytelling)
.streamlit/config.toml               # tema warna biru laut
data/multivariat_provinsi.csv        # 38 provinsi x 8 variabel (data ASLI, lengkap)
data/geospasial_kabkota.csv          # 514 kab/kota + centroid lat/lon (data ASLI)
data/kabkota_simplified.geojson      # batas wilayah 514 kab/kota (disederhanakan, 5MB)
data/aliran_ekspor_negara.csv        # ekspor 11 negara x 2012-2025 (data ASLI, long format)
data/ekspor_provinsi_tahun.csv       # ekspor 38 provinsi x 2019-2026 (data ASLI, long format)
requirements.txt
```

## Sumber data (lengkapi detail sitasi sebelum submit!)
Ketiga file sumber (`multivariat.xlsx`, `produksi_perikanan_tangkap_2024.xlsx`,
`ekspor.xls`) kamu kumpulkan sendiri dari BPS. **Saya tidak tahu persis judul
tabel, URL, dan tanggal akses aslinya** — soal mewajibkan ini dicantumkan di
setiap visualisasi (poin 2b) dan di makalah. Isi bagian `[...]` di
`draf_makalah_IEEE.md` dan di caption aplikasi (`app.py` baris dekat
`st.caption("Sumber: BPS...")`) dengan:
- Judul tabel/publikasi BPS persis (mis. "Statistik Kelautan dan Perikanan
  Indonesia 2024", "Ekspor Menurut Kode HS dan Negara Tujuan", dst.)
- Tahun data
- URL tabel BPS
- Tanggal kamu mengakses/mengunduhnya

## Batas wilayah (GeoJSON) — cara didapat
`data/kabkota_simplified.geojson` diturunkan dari shapefile batas kab/kota
2020 (repo publik `Alf-Anas/batas-administrasi-indonesia`, berbasis data
Kemendagri), lalu disederhanakan (simplify tolerance 0.02°) dan di-join ke
`kode_wilayah` dari data produksimu. **481 dari 514 kab/kota (93,6%) cocok**;
33 sisanya (mayoritas provinsi pemekaran Papua: Papua Tengah, Papua
Pegunungan, dll., karena kode wilayahnya berbeda dari shapefile lama + 3-4
kab/kota lain yang kodenya berubah seperti Kota Dumai) tidak tergambar warna
di peta. Ini **data pendukung non-BPS yang sah dipakai** (soal poin 2a) —
sebutkan di makalah bagian Metodologi & Keterbatasan.

## ⚠️ Yang perlu kamu cek/lengkapi sebelum submit

1. **Sitasi sumber** (lihat di atas) — wajib di setiap visualisasi & makalah.
2. **Data ekspor baru 11 entitas** (10 negara + "Lainnya"), padahal soal minta
   ≥15 entitas asal/tujuan. Cari tabel BPS "Ekspor menurut Negara Tujuan"
   yang lebih rinci (biasanya ada versi dengan 20-30 negara, bukan yang sudah
   diringkas ke "10 negara utama + lainnya") untuk menggantikan `data/aliran_ekspor_negara.csv`.
3. **Catatan Sankey 3-lapis**: total volume sisi provinsi dan sisi negara berasal dari dua tabel BPS berbeda cakupan sehingga tidak otomatis sama — sudah diberi catatan transparan di aplikasi, tapi jelaskan juga di makalah bagian Metodologi.
4. **33 kab/kota tidak match ke peta** — opsional: cari kode wilayah yang
   benar untuk kab/kota pemekaran Papua agar makin lengkap, atau cukup
   jelaskan di bagian keterbatasan makalah (ini valid secara akademik, bukan
   kesalahan fatal).
5. Cek ulang bahwa variabel yang dipilih untuk PCA (`data/multivariat_provinsi.csv`)
   sudah sesuai dengan yang ingin kamu tonjolkan — bisa ditambah/dikurangi.

## Deployment (Streamlit Community Cloud)
1. Push folder ini ke repo GitHub publik (lihat langkah git di bawah).
   > Catatan ukuran: `kabkota_simplified.geojson` ~5 MB, masih jauh di bawah
   > limit GitHub (100 MB/file) dan Streamlit Cloud — aman di-push langsung.
2. Buka https://share.streamlit.io → "New app" → pilih repo & branch →
   file utama `app.py` → Deploy.
3. Salin URL yang diberikan (format `https://<nama>.streamlit.app`) — ini
   alamat proyek yang dicantumkan di akhir makalah IEEE.
4. Pastikan tautan tetap aktif sampai nilai akhir diumumkan.

## Push ke GitHub
```bash
git init
git add .
git commit -m "UAS Visdat: dashboard perikanan tangkap Indonesia"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo>.git
git push -u origin main
```

## Deklarasi penggunaan AI
Sesuai poin 7 soal (integritas akademik): proyek ini dibantu alat AI
(Claude) untuk pembersihan data, kerangka kode aplikasi, pemrosesan
GeoJSON, dan template makalah. Data BPS, verifikasi angka, interpretasi
hasil, dan keputusan desain visualisasi akhir tetap menjadi tanggung jawab
mahasiswa. Cantumkan kalimat deklarasi serupa di bagian Metodologi makalah.

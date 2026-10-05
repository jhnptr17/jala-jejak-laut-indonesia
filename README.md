# JALA — Jejak Laut Indonesia

Dasbor *data storytelling* produksi dan ekspor perikanan tangkap Indonesia berbasis data BPS. Pembaca menggulir dari profil 38 provinsi, ke sebaran 514 kabupaten/kota, hingga arus ekspor ke negara tujuan.

**Aplikasi:** [URL-APLIKASI].streamlit.app (tanpa login, dapat dibuka di laptop dan ponsel)
**Repositori:** https://github.com/[USERNAME]/jala-jejak-laut

Proyek UAS Visualisasi Data dan Informasi (K203407), Politeknik Statistika STIS, TA 2025/2026.
Penulis: Johana Putri Natasya Sitorus (NIM 222313150, kelas 3SD2). Dosen pengampu: Siti Mariyah, Ph.D. dan Farid Ridho, M.T.

---

## Tiga topik visualisasi

| Topik | Teknik | Interaksi |
|---|---|---|
| Berdimensi tinggi (multivariat) | PCA biplot, parallel coordinates, heatmap terklaster skor-z, klaster K-Means | Brushing dan linking antar tampilan, pemilih jumlah klaster (2–8), tooltip |
| Geospasial | Choropleth rasio dan proportional symbol (514 kab/kota) | Pemilih jenis peta dan indikator, zoom, pan, tooltip, legenda kelas |
| Aliran (*flow*) | Sankey tiga lapis (provinsi, Indonesia, negara), flow map dunia, tren garis | Pemilih tahun, tooltip |

Cakupan dibandingkan ketentuan minimal (Lampiran A soal):

| Topik | Ketentuan minimal | Pada proyek ini |
|---|---|---|
| Multivariat | ≥ 8 variabel, 34 unit, 1 teknik reduksi + 2 teknik lain, brushing dan linking | 8 variabel, 38 provinsi, PCA + parallel coordinates + heatmap, brushing dan linking |
| Geospasial | Kab/kota (± 500 unit), 2 jenis peta, klasifikasi dijustifikasi, choropleth memakai rasio | 514 kab/kota, choropleth dan proportional symbol, kuantil/kelas manual, rasio Rp/kg dan % laut |
| Aliran | ≥ 15 entitas, 2 teknik, volume dan arah dikodekan, filter | 25 provinsi asal dan 11 negara tujuan, Sankey dan flow map, filter tahun |

## Pilihan desain geospasial

- **Choropleth hanya memakai rasio**, supaya luas wilayah dan besarnya produksi tidak otomatis memenangkan peta. Indikatornya: harga rata-rata ikan (nilai produksi ÷ volume produksi, Rp per kg) dan porsi tangkapan laut (produksi laut ÷ produksi total, %).
- **Proportional symbol memakai angka absolut** (produksi total, laut, perairan darat, nilai produksi), sehingga pembaca bisa membandingkan peta rasio dengan peta besaran.
- **Klasifikasi lima kelas diskret.** Harga memakai kuantil karena sebarannya sangat miring (median sekitar Rp29.800 per kg, maksimum jutaan rupiah). Porsi laut memakai kelas manual karena sebarannya dua kutub (149 kab/kota 0% dan 159 kab/kota 100%), sehingga kuantil menghasilkan batas kelas kembar.
- **Abu-abu** untuk 30 kab/kota tanpa produksi, karena rasionya tidak terdefinisi.
- **Palet** ColorBrewer YlGnBu (sequential, aman buta warna) untuk peta kelas, Okabe–Ito untuk warna kategori, dan diverging merah–biru untuk heatmap skor-z.

## Sumber data

Data utama bersumber dari BPS. Setiap visualisasi di aplikasi memuat keterangan *Sumber: BPS* beserta tahun datanya.

| Data | Unit | Tahun | Sumber | URL | Diakses |
|---|---|---|---|---|---|
| Volume dan nilai produksi perikanan tangkap menurut provinsi dan jenis penangkapan | 38 provinsi | 2024 | BPS | [URL-TABEL] | 3 Oktober 2026 |
| Volume dan nilai produksi perikanan tangkap menurut kabupaten/kota | 514 kab/kota | 2024 | BPS | [URL-TABEL] | 3 Oktober 2026 |
| Jumlah nelayan, kapal, dan rumah tangga perikanan | 38 provinsi | 2024 | KKP (berbasis Sensus Pertanian BPS 2023) | https://portaldata.kkp.go.id/ | 3 Oktober 2026 |
| PDRB perikanan menurut provinsi | 38 provinsi | 2024 | BPS | [URL-TABEL] | 3 Oktober 2026 |
| Ekspor menurut provinsi asal | 38 provinsi | 2019–2026 | KKP | https://portaldata.kkp.go.id/ | 3 Oktober 2026 |
| Ekspor menurut negara tujuan | 10 negara + Lainnya | 2012–2025 | BPS | [URL-TABEL] | 3 Oktober 2026 |

Data pendukung non-BPS: batas wilayah kab/kota 2020 (berbasis data Kemendagri), diturunkan dari repositori publik `Alf-Anas/batas-administrasi-indonesia`, disederhanakan (toleransi 0,02°) dan digabung lewat kode wilayah empat digit. Batas negara pada flow map berasal dari Plotly/Natural Earth.

> Judul tabel BPS yang persis dan URL lengkap dicantumkan di Daftar Pustaka makalah.

## Data terolah

Aplikasi hanya membaca berkas terolah di `data/`:

| Berkas | Isi |
|---|---|
| `multivariat_provinsi.csv` | 38 provinsi × 8 variabel numerik (nelayan, kapal, RTP, produksi laut, produksi perairan darat, nilai produksi, PDRB perikanan, volume ekspor 2025) |
| `geospasial_kabkota.csv` | 514 kab/kota: kode wilayah, produksi dan nilai produksi (laut, perairan darat, total), koordinat titik pusat |
| `kabkota_simplified.geojson` | Batas wilayah kab/kota yang disederhanakan |
| `aliran_ekspor_negara.csv` | Volume (ton) dan nilai FOB (ribu USD) menurut negara tujuan, 2012–2025 |
| `ekspor_provinsi_tahun.csv` | Volume ekspor (ton) menurut provinsi asal, 2019–2026 |

Ringkasan pra-pemrosesan: baris total dan baris kosong dibuang, nama wilayah diseragamkan, simbol strip dianggap nol hanya bila bermakna tidak ada produksi (data tidak tersedia tidak diubah menjadi nol), dan variabel multivariat distandardisasi dengan skor-z sebelum PCA dan K-Means. Dua rasio choropleth dihitung di `app.py` saat data dimuat (`load_geospasial`).

## Struktur repositori

```
app.py                          # aplikasi Streamlit
requirements.txt                # dependensi
.streamlit/config.toml          # tema warna
assets/                         # logo BPS dan KKP
data/                           # data terolah (lihat tabel di atas)
README.md
```

## Menjalankan secara lokal

```bash
git clone https://github.com/[USERNAME]/jala-jejak-laut.git
cd jala-jejak-laut
pip install -r requirements.txt
streamlit run app.py
```

Butuh koneksi internet untuk peta dasar (Carto) dan Google Fonts. Tanpa internet, font memakai cadangan sistem dan peta dasar tidak tampil.

## Deployment

Aplikasi di-deploy lewat Streamlit Community Cloud dari repositori ini (branch `main`, berkas utama `app.py`) dan dapat diakses publik tanpa login maupun instalasi.

## Keterbatasan

- Data negara tujuan baru mencakup 10 negara dan agregat *Lainnya*.
- 17 dari 514 kab/kota (terutama di Papua dan Papua Barat) tidak tergambar pada peta karena kode wilayahnya tidak cocok dengan batas wilayah 2020.
- Total sisi provinsi dan sisi negara pada Sankey berasal dari dua tabel BPS dengan cakupan berbeda, sehingga lebar pita hanya sebanding di dalam satu sisi.
- Choropleth belum memakai rasio per penduduk atau per luas wilayah. Harga ekstrem (di atas Rp100.000 per kg) pada 31 kab/kota diduga salah catat atau salah satuan dan belum dikoreksi.
- Jumlah klaster ditentukan pengguna, sehingga hasilnya subjektif, dan PCA hanya menangkap hubungan linear.
- Belum ada uji pengguna; evaluasi rancangan bersifat heuristik.

## Deklarasi penggunaan AI

Penulis menggunakan Claude (Anthropic) sebagai alat bantu untuk menyusun kerangka kode aplikasi, membantu pemrosesan GeoJSON, serta menyunting narasi aplikasi dan draf makalah. Pengumpulan data BPS, verifikasi angka, interpretasi, dan keputusan akhir rancangan merupakan tanggung jawab penuh penulis.

## Kredit

Data: Badan Pusat Statistik dan Kementerian Kelautan dan Perikanan. Batas wilayah: Kemendagri via `Alf-Anas/batas-administrasi-indonesia`. Peta dasar: Carto/OpenStreetMap. Pustaka: Streamlit, Plotly, Altair, pandas, scikit-learn.

# 📊 Analytics & BI Module – GEAR System

## Branch

`feature/analytics`

---

## 📖 Deskripsi

Branch ini berisi pengembangan **Modul Analitik & Business Intelligence** pada sistem GEAR. Modul ini berfokus pada penyediaan wawasan strategis, prediksi tren pasar, evaluasi performa operasional (Sales & Supplier), serta rekomendasi keputusan otomatis bagi Owner untuk menjaga profitabilitas (margin) dan pertumbuhan bisnis secara berkelanjutan.

---

# 🎯 Scope Fitur

## 1. Predictive Margin Calculator

### Deskripsi

Dashboard otomatis yang berfungsi menghitung laba bersih secara real-time dan memberikan rekomendasi harga jual dinamis untuk menjaga stabilitas margin keuntungan perusahaan di tengah fluktuasi harga bahan baku.

### Fungsionalitas

- Kalkulasi otomatis _Cost of Goods Sold_ (COGS) berdasarkan harga rata-rata stok saat ini.
- Monitoring margin keuntungan bersih (Target: Rp500/kg).
- Sistem rekomendasi harga jual baru ("Suggested Price") jika harga krosok naik.
- Simulasi skenario keuntungan (_What-If Analysis_).

---

## 2. Market Price Intelligence (NLP)

### Deskripsi

Bot cerdas yang mengumpulkan dan menganalisis data tren harga pasar (garam, plastik, iodium) untuk memberikan peringatan dini terkait pergerakan harga komoditas.

### Fungsionalitas

- Input manual atau scraping data harga pasar eksternal.
- Analisis sentimen berita/pasar menggunakan NLP (_Natural Language Processing_).
- Indikator tren harga visual: `Cenderung Naik`, `Stabil`, `Cenderung Turun`.
- Prediksi jangka pendek (e.g., "Harga cenderung naik 2 minggu lagi").
- Rekomendasi waktu pembelian stok (_Stockpiling Alert_).

---

## 3. Sales Performance Analytics

### Deskripsi

Visualisasi data komprehensif untuk mengevaluasi kinerja tim sales, tidak hanya dari segi omzet tetapi juga kesehatan piutang yang dihasilkan.

### Fungsionalitas

- Leaderboard penjualan (Volume & Revenue) per Sales.
- Analisis rasio piutang macet per Sales (_Bad Debt Ratio_).
- Grafik pencapaian target individu vs realisasi.
- Analisis efektivitas rute/wilayah penjualan.

---

## 4. Year-on-Year (YoY) Trend Comparison

### Deskripsi

Grafik perbandingan performa bisnis antar periode waktu untuk memantau pertumbuhan tahunan dan mengidentifikasi pola siklus musiman.

### Fungsionalitas

- Grafik garis komparatif: Penjualan Bulan Ini vs Bulan yang Sama Tahun Lalu.
- Deteksi anomali musiman (misal: dampak musim hujan/kemarau terhadap penjualan).
- Perhitungan persentase pertumbuhan (_Growth Rate_).
- Identifikasi bulan-bulan _peak season_ dan _low season_.

---

## 5. Supplier Quality Scoring

### Deskripsi

Sistem rating objektif untuk mengevaluasi kinerja supplier berdasarkan data historis penerimaan barang, guna memastikan kualitas bahan baku yang konsisten.

### Fungsionalitas

- Scoring otomatis berdasarkan ketepatan waktu pengiriman.
- Penilaian kualitas fisik bahan baku (Parameter: Putih/Kering vs Kuning/Basah).
- Riwayat retur barang per supplier.
- Ranking supplier terbaik untuk rekomendasi _Purchase Order_.

---

## 6. Customer Loyalty & Retention Monitor

### Deskripsi

Sistem pemantauan perilaku pembelian pelanggan untuk menjaga retensi, mengidentifikasi pelanggan yang berisiko hilang, dan mendukung strategi pemasaran yang tepat sasaran.

### Fungsionalitas

- Analisis frekuensi dan volume pembelian pelanggan (_RFM Analysis_).
- Deteksi otomatis pelanggan tidak aktif/dorman (≥3 bulan tidak ada transaksi).
- Segmentasi pelanggan (e.g., Loyal, Berisiko, Pasif).
- Rekomendasi program diskon atau strategi reaktivasi pelanggan.

---

# 📈 Expected Outcome

- Keputusan penetapan harga jual lebih cepat dan akurat menjaga margin.
- Risiko kerugian akibat fluktuasi harga bahan baku dapat diminimalisir.
- Evaluasi tim sales lebih objektif (berdasarkan omzet bersih dari macet).
- Kualitas supply chain meningkat melalui evaluasi supplier berbasis data.
- Strategi retensi pelanggan lebih proaktif dan tepat sasaran.

# 📊 Finance Module – GEAR System

## Branch
`feature/finance`

---

## 📖 Deskripsi

Branch ini berisi pengembangan **Modul Keuangan & Piutang** pada sistem GEAR.  
Modul ini berfokus pada transparansi arus kas, pengelolaan invoice, monitoring piutang, serta pencatatan biaya operasional secara terstruktur dan terintegrasi dengan modul Order dan Sales.

---

# 🎯 Scope Fitur

## 1. Digital Invoice & Debt Aging

### Deskripsi
Fitur untuk menghasilkan invoice otomatis berdasarkan transaksi penjualan serta memantau status pembayaran dan umur piutang (aging).

### Fungsionalitas
- Generate invoice otomatis dari data order
- Penentuan tanggal jatuh tempo (due date)
- Perhitungan sisa tagihan otomatis
- Klasifikasi aging piutang:
  - 0–30 hari
  - 31–60 hari
  - 61–90 hari
  - >90 hari
- Penandaan invoice overdue
- Monitoring status pembayaran: `UNPAID`, `PARTIAL`, `PAID`

---

## 2. Payment Confirmation

### Deskripsi
Fitur untuk mengunggah dan memvalidasi bukti pembayaran dari sales, serta memperbarui status invoice secara otomatis.

### Fungsionalitas
- Upload bukti transfer / foto nota
- Penyimpanan file pembayaran
- Update nominal pembayaran (`paid_amount`)
- Perhitungan sisa tagihan otomatis
- Perubahan status invoice berdasarkan total pembayaran

---

## 3. Operational Expense Tracker

### Deskripsi
Modul pencatatan biaya operasional di luar bahan baku untuk membantu monitoring arus kas perusahaan.

### Fungsionalitas
- Input data pengeluaran
- Kategori biaya (Upah, Bensin, Listrik, dll)
- Penyimpanan tanggal dan nominal biaya
- Rekap pengeluaran per bulan
- Ringkasan total pengeluaran

---

# 📈 Expected Outcome

- Monitoring piutang lebih transparan
- Mengurangi risiko piutang macet
- Arus kas tercatat secara sistematis
- Owner dapat mengambil keputusan berbasis data keuangan


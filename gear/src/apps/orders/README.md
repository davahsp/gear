Orders & Logistics Module – GEAR System

Branch
`feat/orders`

    Deskripsi
    Branch ini berisi pengembangan *Modul Manajemen Pesanan & Logistik* pada sistem GEAR. Modul ini dirancang untuk mendigitalisasi seluruh siklus pemesanan (Order-to-Cash), mulai dari pengecekan stok oleh sales di lapangan, input pesanan otomatis via WhatsApp, hingga pencetakan dokumen jalan dan pelacakan status pengiriman. Tujuannya adalah memangkas waktu administrasi manual dan menghilangkan *human error* dalam pencatatan transaksi.

Scope Fitur
1. Real-Time Stock Query (WhatsApp Bot)
    Deskripsi
    Fitur interaktif berbasis bot WhatsApp yang memungkinkan Sales Lapangan untuk mengecek ketersediaan stok di gudang secara *real-time* tanpa perlu menelepon admin, memastikan janji stok ke pelanggan selalu akurat.

    Fungsionalitas
    - Integrasi Webhook WhatsApp untuk merespons *keyword* tertentu (misal: "Cek Stok").
    - *Query* langsung ke *database* inventori untuk mendapatkan data stok fisik terkini.
    - Pemisahan kategori stok (Garam Halus vs Garam Kasar) dalam balasan pesan.
    - Indikator stok menipis (Low Stock Alert) pada balasan pesan.


2. Instant Order Entry
    Deskripsi
    Sistem input pesanan otomatis yang memproses pesan teks standar dari WhatsApp menjadi data transaksi digital yang valid di sistem, mengurangi risiko kesalahan catat atau pesanan terselip.

    Fungsionalitas
    - *Parsing* format pesan otomatis (Regex: `PESAN [Nama Toko] [SKU] [Qty]`).
    - Validasi stok otomatis (Order ditolak jika Stok < Qty Pesan).
    - *Booking* stok otomatis saat pesanan berhasil divalidasi.
    - Generasi ID Transaksi unik dan balasan konfirmasi instan ke Sales.


3. Automated PDF Surat Jalan
    Deskripsi
    Generator dokumen otomatis yang mengubah data pesanan menjadi Surat Jalan (Delivery Order) format PDF standar perusahaan, siap cetak untuk diserahkan kepada supir.

    Fungsionalitas
    - Konversi data transaksi menjadi dokumen PDF siap cetak.
    - Layout standar mencakup: Logo Perusahaan, Detail Penerima, Daftar Barang, dan Kolom Tanda Tangan.
    - Pencantuman QR Code unik pada dokumen untuk validasi digital.
    - Fitur unduh dokumen massal (*Batch Download*) untuk efisiensi admin gudang.


4. Driver Assignment & Status Tracking
    Deskripsi
    Fitur manajemen logistik untuk menugaskan pengiriman kepada armada internal atau ekspedisi eksternal, serta memantau status perjalanan barang hingga sampai ke tangan pelanggan.

    Fungsionalitas
    - Penugasan (Assign) Driver Internal atau Ekspedisi ke ID Transaksi tertentu.
    - Pencatatan Plat Nomor Kendaraan untuk keamanan.
    - Update status transaksi berjenjang (*Siap Kirim* ➝ *On Delivery* ➝ *Selesai*).
    - Riwayat pengiriman per Driver untuk audit kinerja logistik.


5. Sales Order Validation & Monitoring
    Deskripsi
    Dashboard admin untuk memantau seluruh pesanan yang masuk dari bot, memberikan kontrol penuh kepada admin untuk memvalidasi atau membatalkan pesanan yang tidak sesuai.

    Fungsionalitas
    - Tabel *Live Monitoring* pesanan masuk dari WhatsApp.
    - Fitur *Edit Order* jika terjadi kesalahan input dari Sales.
    - Validasi manual untuk pesanan dengan metode pembayaran Tempo (Kredit).
    - Log aktivitas perubahan status pesanan (*Audit Trail*).

Expected Outcome
-  **Kecepatan:** Waktu pemrosesan pesanan berkurang dari 15-20 menit (manual) menjadi < 1 menit (otomatis).
- **Akurasi:** Mengeliminasi kesalahan pembacaan tulisan tangan atau salah dengar di telepon hingga 0%.
- **Transparansi:** Sales dan Admin memiliki satu sumber data kebenaran (*Single Source of Truth*) mengenai status stok dan pesanan.
- **Profesionalitas:** Dokumen pengiriman (Surat Jalan) terstandarisasi dan terlihat lebih profesional di mata pelanggan.
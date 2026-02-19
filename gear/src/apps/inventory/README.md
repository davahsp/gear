📦 Inventory Module – GEAR System

Branch
feature/inventory

📖 Deskripsi
Branch ini berisi pengembangan Modul Inventori & Operasional Gudang pada sistem GEAR.

Modul ini dirancang untuk menjembatani aktivitas lapangan (gudang dan sales) dengan database pusat secara real-time. Fokus utamanya adalah memastikan akurasi stok, otomatisasi dokumen pengiriman, serta meminimalkan kesalahan pencatatan manual melalui antarmuka WhatsApp Bot yang ringan dan cepat.

🎯 Scope Fitur
1. Real-Time Stock Query & Reservation
Deskripsi Fitur akses cepat bagi tim sales untuk memeriksa ketersediaan stok tanpa perlu menghubungi admin gudang secara manual.

Fungsionalitas

Query Otomatis: Menampilkan daftar stok per SKU (halus/kasar) via perintah pesan "STOK".

Instant Order Entry: Pencatatan pesanan langsung dari lokasi pelanggan melalui format WhatsApp.

Stock Locking: Melakukan reservasi kuantitas barang segera setelah order tervalidasi (mencegah overselling).

Automated PDF Surat Jalan: Auto-generate dokumen pengiriman (PDF) yang dikirim langsung ke WA admin gudang.

2. Production & Material Inflow Logging
Deskripsi Sistem pembaruan saldo stok yang berasal dari aktivitas masuknya bahan baku maupun hasil produksi harian.

Fungsionalitas

Material Inflow: Pencatatan kedatangan garam krosok (bahan baku) beserta identitas supplier.

Production Daily Report: Update stok siap jual (produk jadi) berdasarkan hasil repacking harian oleh pengawas gudang.

Traceability: Rekam jejak asal barang dan histori tanggal produksi untuk keperluan audit internal.

3. Reject & Damage Tracking
Deskripsi Fitur penyesuaian stok berdasarkan kondisi fisik barang di lapangan untuk menjaga sinkronisasi data sistem dengan fisik gudang.

Fungsionalitas

Kategorisasi Kerusakan: Pencatatan alasan pengurangan stok (plastik pecah, garam kuning, basah, dll).

Inventory Adjustment: Pengurangan saldo stok secara otomatis tanpa melalui proses transaksi penjualan.

Reporting: Menyediakan data kehilangan operasional untuk evaluasi kualitas bahan baku/kemasan.

4. Inventory Intelligence & Planning
Deskripsi Pemanfaatan data historis untuk mengoptimalkan ketersediaan stok di masa mendatang.

Fungsionalitas

YoY Trend Comparison: Visualisasi grafik perbandingan stok dan penjualan tahun lalu untuk menghindari penumpukan barang.

Market Price Monitoring: Analisis tren harga bahan baku untuk menentukan waktu pembelian stok (re-stocking) yang paling efisien.

📈 Expected Outcome
Akurasi Stok 100%: Menghilangkan selisih data antara catatan kantor dan kondisi fisik di gudang.

Efisiensi Operasional: Mempercepat proses dari pesanan masuk hingga cetak surat jalan menjadi hitungan detik.

Aksesibilitas Tinggi: Tim lapangan dapat mengelola inventori hanya melalui perintah teks sederhana (WhatsApp).

Perencanaan Akurat: Owner dapat melakukan pembelian bahan baku di waktu yang tepat berdasarkan tren harga dan kebutuhan historis.
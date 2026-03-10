# Setup Data untuk Inventory

## 1. Load Raw Materials Fixture

Untuk memuat 4 bahan baku yang sudah didefinisikan (Garam Krosok, Iodium, Plastik, Karung), jalankan:

```bash
python manage.py loaddata initial_raw_materials
```

Raw materials yang akan dimuat:
- **Garam Krosok** (pk=1) → unit: kg
- **Iodium** (pk=2) → unit: kg
- **Plastik** (pk=3) → unit: pcs
- **Karung** (pk=4) → unit: pcs

## 2. Buat Supplier

Supplier wajib dibuat melalui Django Admin (`/admin/`) atau Django Shell.

### Via Django Admin:
1. Buka `http://localhost:8000/admin/`
2. Masuk dengan akun superuser
3. Klik pada **Suppliers** di bagian Inventory
4. Klik **Add Supplier**
5. Isi form:
   - **Name**: Nama supplier (misal: "PT. Garam Madura")
   - **Phone Number**: Nomor telp supplier
   - **Email** (optional): Email supplier
   - **Address** (optional): Alamat supplier
6. Klik **Save**

### Via Django Shell:
```bash
python manage.py shell
```

```python
from inventory.models import Supplier

Supplier.objects.create(
    name="PT. Garam Madura",
    phone_number="08123456789",
    email="contact@garamadura.com",
    address="Jl. Madura No. 123, Surabaya"
)

Supplier.objects.create(
    name="CV. Iodium Nusantara",
    phone_number="08234567890"
)

# Dan seterusnya...
```

## 3. Verifikasi Form

Setelah data dimuat, akses form di:
```
http://localhost:8000/inventory/inbounds/add/
```

Form akan menampilkan:
- ✅ Dropdown Bahan Baku dengan 4 pilihan
- ✅ Satuan otomatis berubah saat memilih bahan baku
- ✅ Dropdown Supplier dengan semua supplier yang sudah dibuat
- ✅ Tombol "+ Tambah" untuk menambah kartu transaksi baru

## 4. Testing Multi-Card Form

1. Isi form pertama dengan data lengkap
2. Klik "+ Tambah" untuk menambah kartu kedua
3. Isi kartu kedua dengan data berbeda
4. Klik "Simpan" → Pilih "Ya, Simpan" di konfirmasi
5. Verifikasi di list transaksi (`/inventory/inbounds/`) bahwa kedua transaksi tersimpan

Note: Satuan akan otomatis update ketika:
- Form pertama kali dimuat (dari fixture)
- User memilih bahan baku di dropdown
- Kartu baru ditambahkan

# Multi-Card Form dengan Satuan Otomatis - Implementation Complete

## Ringkasan Perubahan

Implementasi form multi-card dengan satuan otomatis berdasarkan jenis bahan baku telah selesai. Berikut adalah perubahan yang dilakukan:

### 1. **Backend Changes**

#### `views.py` - Function `inbound_add()`
- Menambahkan `unit` field ke JSON representation untuk raw materials
- Raw materials dikirim ke template dengan format: `[{'id': pk, 'name': name, 'unit': unit}]`
- Suppliers juga dikirim ke template untuk dropdown dinamis

**Before:**
```python
raw_materials_json = [{'id': rm.pk, 'name': rm.name} for rm in raw_materials]
```

**After:**
```python
raw_materials_json = [{'id': rm.pk, 'name': rm.name, 'unit': rm.unit} for rm in raw_materials]
```

### 2. **Frontend Changes**

#### `inbound_add.html` - Template
- **Struktur Jumlah + Satuan**: Menampilkan input quantity di sebelah display satuan (unit)
- **Unit Display**: Elemen `<span class="unit-display">` menampilkan satuan secara read-only
- **Initial Cards**: Semua card (baik initial maupun dinamis) memiliki struktur yang sama

**Before (Quantity hanya dengan helper text):**
```html
<input type="number" name="..." placeholder="ex: 2000" class="...">
<p class="mt-1 text-xs text-gray-400">Masukkan dalam satuan kg (/) pcs</p>
```

**After (Quantity + Unit Display):**
```html
<div class="flex gap-3">
    <input type="number" name="..." placeholder="ex: 2000" class="flex-grow ...">
    <div class="flex-shrink-0 flex items-center px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg ...">
        <span class="unit-display">kg</span>
    </div>
</div>
```

#### `inbound_add.html` - JavaScript

**Fungsi Baru: `updateUnitForCard(card)`**
- Mengupdate unit display di card tertentu berdasarkan pilihan raw_material
- Membaca `dataset.unit` dari selected option
- Dipanggil saat page load dan saat user mengubah select

**Perubahan: `populateSelects()`**
- Tambahkan `data-unit` attribute ke setiap option (dari RAW_MATERIALS JSON)
- Tambahkan event listener `change` pada setiap raw_material select
- **Penting**: Panggil `updateUnitForCard()` untuk initial cards saat page load

**Perubahan: `handleAddCard()`**
- Set `data-unit` attribute pada options yang baru dibuat
- Tambahkan event listener pada raw_material select untuk update unit
- Unit display otomatis muncul dengan default "kg"

### 3. **Data Fixture**

File: `apps/inventory/fixtures/initial_raw_materials.json`

Fixture JSON yang berisi 4 raw materials dengan unit yang tepat:

```json
[
  {
    "model": "inventory.rawmaterial",
    "pk": 1,
    "fields": {
      "name": "Garam Krosok",
      "unit": "kg",
      "qty_in_stock": 0,
      "last_restocked": null
    }
  },
  ...
]
```

### 4. **Setup Instructions**

File: `apps/inventory/SETUP_DATA.md`

Dokumentasi lengkap untuk:
- Load raw materials fixture
- Create suppliers via Django admin atau shell
- Verify form functionality
- Testing multi-card workflow

---

## Cara Menggunakan

### Step 1: Load Fixture Data
```bash
cd gear/src
python manage.py loaddata initial_raw_materials
```

### Step 2: Buat Supplier (via Django Admin atau Shell)
Akses `/admin/` dan tambahkan supplier, atau gunakan shell:
```bash
python manage.py shell
from inventory.models import Supplier
Supplier.objects.create(name="PT. Garam Madura", phone_number="08123456789")
```

### Step 3: Test Form
1. Akses `http://localhost:8000/inventory/inbounds/add/`
2. Dropdown Bahan Baku: Pilih salah satu dari 4 pilihan
3. Unit Display: Akan otomatis update ke satuan yang tepat
   - Garam Krosok → **kg**
   - Iodium → **kg**
   - Plastik → **pcs**
   - Karung → **pcs**
4. Isi supplier, jumlah, dan tanggal
5. Klik "+ Tambah" untuk menambah kartu kedua
6. Klik "Simpan" untuk submit

---

## Fitur yang Sudah Diimplementasi

✅ **Multi-Card Form**
- Tambah/hapus kartu transaksi
- Setiap kartu independent dengan data sendiri
- Batch processing: semua valid forms tersimpan sekaligus

✅ **Satuan Otomatis**
- Terintegrasi dengan database RawMaterial.unit
- Update otomatis saat user memilih bahan baku
- Display read-only (user tidak perlu input satuan manual)
- Work pada initial cards dan dynamically added cards

✅ **Dropdown Dinamis**
- Raw Material: 4 pilihan dari fixture
- Supplier: Semua supplier dari database
- Sorted alphabetically (untuk future: jika diperlukan)

✅ **Validasi Client-Side**
- Check minimal satu kartu terisi
- Check semua field terisi jika kartu ada data
- Show error message jika validasi gagal

✅ **Stock Update**
- Saat submit, qty_in_stock raw material otomatis bertambah
- last_restocked dan supplier.last_transaction terupdate

---

## Error Handling

Jika terjadi error saat setup:

### Error: "No RawMaterial found during populating"
**Solusi**: Pastikan fixture sudah di-load dengan `python manage.py loaddata initial_raw_materials`

### Error: "Dropdown kosong"
**Solusi**: Pastikan JavaScript `populateSelects()` dipanggil saat DOMContentLoaded. Check browser console untuk JavaScript errors.

### Error: Supplier tidak muncul
**Solusi**: Pastikan sudah create supplier via Django admin atau shell.

---

## Notes untuk Developer

1. **RAW_MATERIALS JSONData** di-pass dari view sebagai:
   ```python
   raw_materials_json = [{'id': rm.pk, 'name': rm.name, 'unit': rm.unit} ...
```

2. **Unit Display** menggunakan `dataset.unit` dari selected option, fallback ke "kg"

3. **Event Listener** untuk raw_material select ditambahkan di:
   - `populateSelects()` untuk initial forms
   - `handleAddCard()` untuk dynamically created forms

4. **Validasi** sudah cover:
   - Empty cards (ignored)
   - Partial filled cards (error)
   - Negative/zero quantity (error)

5. **Formset Prefix** adalah "inbound", sehingga nama field adalah `inbound-0-raw_material`, `inbound-1-raw_material`, dll.

---

## Testing Checklist

- [ ] Load fixture: `python manage.py loaddata initial_raw_materials`
- [ ] Create minimal 1 supplier via admin
- [ ] Access `/inventory/inbounds/add/`
- [ ] Verify: Dropdown Bahan Baku ada 4 pilihan
- [ ] Verify: Unit display update saat pilih bahan baku
- [ ] Verify: Klik "+ Tambah" menambah kartu baru
- [ ] Verify: Hapus kartu (X button) berfungsi
- [ ] Verify: Submit form valid → redirect ke list dengan success message
- [ ] Verify: Stock updated di list transaksi atau detail produk
- [ ] Verify: Client validation working (empty form error, partial fill error)

---

Generated: Auto-implementation of multi-card form dengan satuan otomatis

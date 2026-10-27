LANGKAH MEMBUKA PAKET PBIP: Inflasi Indonesia 2026
====================================================================

1. Ekstrak file ZIP ini ke folder lokal (mis. C:\PowerBI\Inflasi).
2. Buka file InflasiIndonesia2026.pbip dengan Power BI Desktop.
3. Saat diminta parameter, klik Edit Parameters atau Transform Data,
   lalu arahkan FolderData ke folder "data" di dalam hasil ekstrak
   (folder berisi 11 file CSV kit).
4. Klik Refresh agar seluruh tabel termuat.
5. Cek cepat angka kunci (Halaman 1: Ringkasan Inflasi):
   - Kartu Inflasi YoY Terbaru harus menunjukkan 3,28
   - Kartu Inflasi MtM Terbaru harus menunjukkan 0,30
   - Kartu IHK Terbaru harus menunjukkan 112,31 (basis 2022=100)
   - Kartu Puncak YoY harus menunjukkan 5,95 (September 2022)
   - Halaman 3: Kota YoY Tertinggi 9,05 (Kab. Minahasa Utara),
     Kota YoY Terendah 1,04 (Kab. Timor Tengah Selatan),
     Jumlah Kota Di Atas Nasional 92, Provinsi Tertinggi 7,59
   - Halaman 4: Jumlah Bulan Deflasi Teramati 11
6. Jika semua cocok, Save As menjadi Inflasi-Indonesia-2026.pbix.

Catatan sentuhan pertama (wajar terjadi):
- Slicer periode mungkin tampil sebagai daftar (list), bukan slider.
  Itu normal untuk data periode kategori.
- Visual peta tidak dipakai (diganti bar terurut) karena visual peta PBIR
  rawan error; disparitas wilayah tetap terbaca jelas dari bar.
- Inflasi adalah persentase resmi BPS: measure memakai AVERAGE, MAX,
  atau MIN, jangan pernah SUM.
- Seri mtm mempunyai celah (bulan yang tidak terkompilasi dari sumber
  resmi); grafik mtm akan menampilkan kekosongan pada bulan tersebut.
  Lihat data/SOURCES.md di repo untuk daftar lengkapnya.

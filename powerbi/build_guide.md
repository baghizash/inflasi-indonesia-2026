# Panduan Merakit Dashboard: Inflasi Indonesia 2026

Hasil akhir: `Inflasi-Indonesia-2026.pbix`.

1. Buka Power BI Desktop, pilih Get Data, Text/CSV, lalu muat SEMUA berkas
   CSV di folder ini (5 fakta dan 6 dimensi).
2. Di Model view, buat relasi satu arah (Single) berikut:
   fact_inflasi_bulanan[bulan_key] ke dim_bulan[bulan_key];
   fact_inflasi_bulanan[tahun_id] ke dim_tahun[tahun_id];
   fact_inflasi_kelompok[bulan_key] ke dim_bulan[bulan_key];
   fact_inflasi_kelompok[kelompok_id] ke dim_kelompok[kelompok_id];
   fact_inflasi_komponen[bulan_key] ke dim_bulan[bulan_key];
   fact_inflasi_komponen[komponen_id] ke dim_komponen[komponen_id];
   fact_inflasi_kota[kota_id] ke dim_kota[kota_id];
   fact_inflasi_kota[bulan_key] ke dim_bulan[bulan_key];
   fact_inflasi_provinsi[provinsi_id] ke dim_provinsi[provinsi_id];
   fact_inflasi_provinsi[bulan_key] ke dim_bulan[bulan_key].
3. Buat measure dari `measures_dax.md`: satu measure per kotak formula,
   tempel persis seperti tertulis (nama measure polos, tanpa tanda sama
   dengan tambahan).
4. Atur format: YoY/MtM/Puncak/Andil sebagai Number 2 desimal; IHK Number
   2 desimal; jumlah sebagai Whole number.
5. Susun 4 halaman mengikuti `dashboard_layout.md`.
6. Verifikasi: kartu Inflasi YoY Terbaru harus menunjukkan 3,28 dan
   Kota YoY Tertinggi 9,05. Bila berbeda, periksa relasi dan filter halaman
   sebelum mengubah measure (lihat tabel verifikasi di measures_dax.md).

-- =====================================================================
-- Kueri SQL: Analisis Inflasi Indonesia 2026
-- Tabel mengikuti berkas CSV di folder data/ dan powerbi/.
-- Contoh ditulis dengan dialek SQL standar (SQLite/DuckDB/PostgreSQL).
-- Semua hasil dapat dicocokkan dengan findings.json.
-- =====================================================================

-- 1. Posisi inflasi terbaru (September 2026)
SELECT periode, ihk, mtm_persen, ytd_persen, yoy_persen
FROM inflasi_nasional_bulanan
ORDER BY periode DESC
LIMIT 1;
-- Harapan: 2026-09 | 112,31 | 0,30 | 2,17 | 3,28

-- 2. Puncak inflasi yoy pada seluruh seri yang terkompilasi
SELECT periode, yoy_persen
FROM inflasi_nasional_bulanan
WHERE yoy_persen IS NOT NULL
ORDER BY yoy_persen DESC
LIMIT 1;
-- Harapan: 2022-09 | 5,95 (bulan kenaikan harga BBM)

-- 3. Inflasi tahunan Desember per tahun (jangkar verifikasi)
SELECT tahun, yoy_persen AS inflasi_desember
FROM inflasi_nasional_bulanan
WHERE bulan = 12 AND yoy_persen IS NOT NULL
ORDER BY tahun;
-- Harapan: 2019 2,72 | 2020 1,68 | 2021 1,87 | 2022 5,51 |
--          2023 2,61 | 2024 1,57 | 2025 2,92

-- 4. Semua bulan deflasi (mtm negatif), terurut dari yang terdalam
SELECT periode, mtm_persen
FROM inflasi_nasional_bulanan
WHERE mtm_persen < 0
ORDER BY mtm_persen;
-- Harapan: 11 bulan; terdalam 2025-02 (-0,48, diskon tarif listrik);
-- era COVID: 2020-07, 2020-08, 2020-09.

-- 5. Kepatuhan pada sasaran BI 2,5% +/- 1% selama 24 bulan terakhir
SELECT
    COUNT(*) AS total_bulan,
    SUM(CASE WHEN yoy_persen BETWEEN 1.5 AND 3.5 THEN 1 ELSE 0 END) AS di_dalam_sasaran,
    SUM(CASE WHEN yoy_persen < 1.5 THEN 1 ELSE 0 END) AS di_bawah,
    SUM(CASE WHEN yoy_persen > 3.5 THEN 1 ELSE 0 END) AS di_atas
FROM inflasi_nasional_bulanan
WHERE periode >= '2024-10' AND yoy_persen IS NOT NULL;
-- Harapan: 24 | 19 | 3 | 2

-- 6. Kemusiman: rata-rata inflasi mtm per bulan kalender
SELECT bulan, nama_bulan,
       ROUND(AVG(mtm_persen), 2) AS rata_rata_mtm,
       COUNT(mtm_persen) AS n_observasi
FROM inflasi_nasional_bulanan
GROUP BY bulan, nama_bulan
ORDER BY bulan;
-- Harapan: tertinggi Maret dan Desember (0,50); terendah Agustus (0,02).

-- 7. Rata-rata inflasi yoy per tahun (hanya tahun dengan cakupan >= 9 bulan)
SELECT tahun, ROUND(AVG(yoy_persen), 2) AS rata_rata_yoy, COUNT(yoy_persen) AS n_bulan
FROM inflasi_nasional_bulanan
GROUP BY tahun
HAVING COUNT(yoy_persen) >= 9
ORDER BY tahun;
-- Harapan: 2023 3,69 | 2024 2,30 | 2025 1,91 | 2026 3,33 (Jan-Sep)

-- 8. Komponen pada September 2026: laju dan andil
SELECT komponen, yoy_persen, mtm_persen, andil_yoy
FROM inflasi_komponen
WHERE periode = '2026-09'
ORDER BY yoy_persen DESC;
-- Harapan: Bergejolak 5,03 | Diatur Pemerintah 3,25 | Inti 2,84
-- Andil terbesar: Inti 1,82 poin.

-- 9. Kelompok pengeluaran penyumbang andil terbesar, September 2026
SELECT kelompok, yoy_persen, andil_yoy
FROM inflasi_kelompok
WHERE periode = '2026-09' AND andil_yoy IS NOT NULL
ORDER BY andil_yoy DESC
LIMIT 5;
-- Harapan teratas: Makanan, Minuman, dan Tembakau (yoy 4,37; andil 1,28).

-- 10. Disparitas kabupaten/kota September 2026
SELECT
    MAX(yoy_persen) AS yoy_tertinggi,
    MIN(yoy_persen) AS yoy_terendah,
    ROUND(MAX(yoy_persen) - MIN(yoy_persen), 2) AS rentang_poin,
    SUM(CASE WHEN yoy_persen > 3.28 THEN 1 ELSE 0 END) AS kota_di_atas_nasional,
    COUNT(*) AS total_kota
FROM inflasi_kota_2026_09;
-- Harapan: 9,05 | 1,04 | 8,01 | 92 | 150

-- 11. Sepuluh kabupaten/kota dengan inflasi yoy tertinggi dan terendah
SELECT kabupaten_kota, ihk, yoy_persen, mtm_persen
FROM inflasi_kota_2026_09
ORDER BY yoy_persen DESC
LIMIT 10;
-- Teratas: Kab. Minahasa Utara 9,05. Gunakan ASC untuk 10 terendah;
-- terbawah: Kab. Timor Tengah Selatan 1,04.

-- 12. Provinsi ekstrem September 2026
SELECT provinsi, yoy_persen, mtm_persen
FROM inflasi_provinsi_2026_09
ORDER BY yoy_persen DESC
LIMIT 3;
-- Harapan teratas: Sulawesi Utara 7,59. Terbawah (ASC): Sumatera Selatan 2,55.

-- 13. Bulan kenaikan BBM: rincian mtm per kelompok, September 2022
SELECT kelompok, mtm_persen
FROM inflasi_kelompok
WHERE periode = '2022-09' AND mtm_persen IS NOT NULL
ORDER BY mtm_persen DESC;
-- Harapan teratas: Transportasi 8,88; terbawah Makanan -0,30.

-- 14. Konsistensi IHK terhadap mtm tercetak, 2023 (kontrol kualitas data)
SELECT a.periode,
       a.ihk AS ihk_bulan_ini,
       b.ihk AS ihk_bulan_lalu,
       ROUND((a.ihk / b.ihk - 1) * 100, 2) AS mtm_dari_ihk,
       a.mtm_persen AS mtm_tercetak
FROM inflasi_nasional_bulanan a
JOIN inflasi_nasional_bulanan b
  ON b.periode = strftime('%Y-%m', date(a.periode || '-01', '-1 month'))
WHERE a.tahun = 2023;
-- Harapan: mtm_dari_ihk sama dengan mtm_tercetak pada 12/12 bulan (2023).

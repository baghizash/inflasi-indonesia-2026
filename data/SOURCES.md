# Sumber Data — Inflasi Indonesia 2026

Seluruh angka dalam proyek ini berasal dari **Badan Pusat Statistik (BPS)**:
rilis bulanan *Berita Resmi Statistik (BRS) "Perkembangan Indeks Harga Konsumen"*,
publikasi *"Dalam Angka"* BPS provinsi (yang memuat tabel nasional), dan siaran pers
BPS. Tidak ada angka tebakan: sel yang tidak terverifikasi dari sumber resmi
dibiarkan kosong dan dicatat di bagian "Keterbatasan" di bawah.

## Dokumen BRS yang dipegang penuh (PDF lokal, diparse per tabel)

| Periode data | No. BRS | Tanggal rilis | Isi yang dipakai |
|---|---|---|---|
| September 2026 | No. 94/10/Th. XXIX | 1 Oktober 2026 | Tabel 1 (kelompok), Tabel 2 (rantai 3 tahun), Gambar 1 (label yoy 2024–2026), Tabel 3–7 (38 provinsi), Tabel 8 (150 kab/kota), Tabel 9 (komponen), Tabel 10 (andil komoditas) |
| November 2025 | No. 105/12/Th. XXVIII | 1 Desember 2025 | Tabel 1 (kelompok), Tabel 9 (komponen), Tabel 2 (rantai Nov 2023–2025) |
| Februari 2026 | No. 22/03/Th. XXIX | 2 Maret 2026 | Tabel 1 (kelompok), Tabel 9 (komponen), Tabel 2 (rantai Feb 2024–2026) |

Unduhan BRS melalui `web-api.bps.go.id/download.php` (tautan unduh di halaman rilis
bps.go.id). Tautan unduh BRS bersifat sementara (kedaluwarsa), karena itu yang
dicatat adalah nomor dan tanggal BRS di atas; PDF-nya tersimpan di arsip kerja proyek.

## Seri per berkas

### `inflasi_nasional_bulanan.csv` (93 bulan, Jan 2019 – Sep 2026)
- **yoy lengkap Jan 2023 – Sep 2026 (45 bulan)**: label tercetak Gambar 1 pada BRS
  (grafik "Tingkat Inflasi Year-on-Year"). Nilai Mei 2026 (3,08), Jun 2026 (3,34),
  dan Jul 2026 (2,88) ditetapkan dari posisi koordinat label pada PDF (ekstraksi bbox),
  konsisten dengan urutan ketinggian labelnya.
- **mtm lengkap 2019 dan 2020**: tabel rekap pada BRS Desember 2020.
- **mtm lengkap 2023**: BPS Provinsi Sulawesi Selatan *Dalam Angka* (kolom nasional);
  konsistensi dengan IHK terbit terverifikasi 12/12 bulan.
- **IHK 2019**: BRS Januari 2020, Tabel 7. **IHK 2023 lengkap**: BRS berkala 2023.
- **Titik 2022**: Sep 2022 dari BRS 3 Oktober 2022 (mtm 1,17%; yoy 5,95%; IHK 112,87);
  Okt–Des 2022 dari BPS Provinsi Jawa Timur *Dalam Angka*; Des 2022 yoy 5,51%.
- **Titik 2024**: mtm Jan (0,04) BRS Jan 2024; Feb–Mar dari Sulsel *Dalam Angka*;
  Jul (−0,18) dan ytd-nya dari rilis BPS Jul 2024; Sep (−0,12) dari rantai Tabel 2 BRS Sep.
- **Titik 2025**: Feb mtm −0,48 dan ytd −1,24 dari rantai Tabel 2 BRS Feb 2026;
  mtm Sep/Okt/Nov/Des dari BRS bulan terkait; ytd Okt 2,10 dari BRS Okt 2025.
- **Titik 2026**: IHK Jan–Apr + Ags–Sep, mtm Feb 0,68 / Mar 0,41 / Apr 0,13 dari BRS
  bulan terkait; komponen inti Mar (yoy 2,52) dan Apr dari BRS Mar/Apr 2026.
- **Basis IHK**: 2018=100 sampai Desember 2023; 2022=100 mulai Januari 2024
  (kolom `basis_ihk`). Laju mtm/yoy dapat dibandingkan lintas pergantian basis;
  level IHK mentah TIDAK disambung lintas basis.

### `inflasi_komponen.csv` (21 baris titik)
Tabel 9 BRS untuk Nov 2025, Feb 2026, Sep 2026 (lengkap: IHK, mtm, ytd, yoy, andil),
ditambah titik terverifikasi: inti Jan 2020 (yoy 2,88; BRS Jan 2020), mtm komponen
Nov & Des 2020 (BRS bulan terkait), inti Sep 2022 (BRS 3 Okt 2022), inti Sep & Okt 2025,
komponen Des 2025 (rilis BPS 5 Jan 2026), inti Mar & Apr 2026.

### `inflasi_kelompok.csv` (52 baris titik)
Tabel 1 BRS untuk Nov 2025, Feb 2026, Sep 2026 (11 kelompok lengkap), ditambah:
mtm 11 kelompok Sep 2022 (BRS 3 Okt 2022); kelompok Makanan Des 2023 (yoy 6,18%,
andil 1,60 — konferensi pers BPS); Des 2025 (Makanan yoy 4,58%, andil 1,33;
kelompok Informasi andil yoy −0,02); tiga kelompok teratas Mar 2026;
mtm Transportasi & Makanan Apr 2026.

### `inflasi_provinsi_2026_09.csv` dan `inflasi_kota_2026_09.csv`
Tabel 3–8 BRS September 2026, diparse dari PDF: 38 provinsi dan 150 kabupaten/kota
(cakupan SBH 2022; sampai 2023 cakupan BPS adalah 90 kota). Validasi silang dengan
prosa BRS: tertinggi Kab. Minahasa Utara 9,05% (IHK 121,70); terendah Kab. Timor
Tengah Selatan 1,04% (IHK 108,48); provinsi tertinggi Sulawesi Utara 7,59%;
terendah Sumatera Selatan 2,55% — semuanya cocok.

## Verifikasi jangkar (inflasi tahunan Desember, yoy)

| Tahun | Jangkar | Hasil kompilasi | Status |
|---|---|---|---|
| 2019 | 2,72% | 2,72% | cocok |
| 2020 | 1,68% | 1,68% (dikonfirmasi siaran pers BI No. 23/2/DKom yang mengutip BPS) | cocok |
| 2021 | 1,87% | 1,87% | cocok |
| 2022 | 5,51% | 5,51% | cocok |
| 2023 | 2,61% | 2,61% | cocok |
| 2024 | 1,57% | 1,57% | cocok |
| 2025 | (tambahan) | 2,92% (rilis BPS 5 Jan 2026) | — |

**Puncak yoy era 2022**: September 2022 sebesar **5,95%** — bulan yang sama dengan
kenaikan harga BBM bersubsidi (3 September 2022). Dugaan awal "Oktober 2022"
tidak terbukti; Oktober 2022 justru mencatat deflasi mtm −0,11%.

## Keterbatasan dan pengecualian (jujur)

1. **yoy bulanan 2019–2022 tidak lengkap** — hanya titik yang terverifikasi
   (Des 2019; Jan, Mei, Sep, Des 2020; Des 2021; Sep, Des 2022). Seri yoy yang
   kontinu tersedia Jan 2023 – Sep 2026 (45 bulan).
2. **mtm 2021 tidak terkompilasi**; mtm 2022 hanya Sep–Des; mtm 2024 hanya
   Jan–Mar, Jul, Sep; mtm 2025 hanya Feb–Mar, Sep–Des; mtm 2026 hanya Jan–Apr, Sep.
   Total mtm terisi 56 dari 93 bulan.
3. **Dua nilai mtm diturunkan dari IHK terbit yang berurutan** (bukan angka cetak):
   Jan 2026 (−0,15 dari IHK 109,92 → 109,75) dan Mar 2025 (1,65 dari 105,48 → 107,22).
   Keduanya ditandai di kolom `catatan` pada CSV nasional.
4. **IHK Oktober 2025 dikecualikan**: angka sekunder 109,00 tidak konsisten dengan
   mtm resmi Oktober 0,28% dari IHK September 108,74 (implikasi 109,04). mtm-nya
   (0,28%) tetap dipakai karena tercetak di rilis BPS.
5. **Angka yoy Agustus 2020 dikecualikan**: dua kutipan sekunder saling bertentangan
   (1,32% vs 1,54%).
6. **Kelompok per Desember hanya terkompilasi untuk Des 2023 dan Des 2025**
   (khususnya kelompok Makanan); seri kelompok bulanan yang lengkap tersedia
   untuk Nov 2025, Feb 2026, dan Sep 2026 dari Tabel 1 BRS.
7. Satu nilai konflik kecil: bahan tayang BPS yang beredar menulis inflasi 2023
   sebesar 3,08% — itu adalah yoy **Juli 2023**, bukan Desember; angka Desember
   resmi 2,61% yang dipakai di sini.

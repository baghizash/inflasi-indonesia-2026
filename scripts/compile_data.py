#!/usr/bin/env python3
"""
compile_data.py — Kompilasi dataset Inflasi Indonesia dari rilis resmi BPS
(BRS "Perkembangan Indeks Harga Konsumen" + publikasi BPS).

Semua angka hardcoded di sini adalah angka yang TERCETAK di rilis BPS
(sumber per seri dicatat di data/SOURCES.md). Tabel 1, Tabel 9, dan tabel
geografi BRS Nov 2025 / Feb 2026 / Sep 2026 dibaca dari hasil parse PDF
lokal (data/raw_parsed/*.json, dibuat oleh scripts/parse_brs.py).

Sel kosong = tidak terverifikasi dari sumber resmi yang berhasil diakses
(tidak pernah diisi tebakan). Dua nilai mtm diturunkan dari IHK terbit
yang berurutan (Jan 2026, Mar 2025) dan ditandai eksplisit di kolom catatan.
"""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw_parsed"
OUT = BASE / "data"
OUT.mkdir(parents=True, exist_ok=True)

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

# ----------------------------------------------------------------------------
# SERI NASIONAL — dicatat per tahun: ihk[12], mtm[12], ytd{bln:val}, yoy[12]
# None = tidak terverifikasi. Basis IHK: 2018=100 s.d. Des 2023; 2022=100 sejak Jan 2024.
# ----------------------------------------------------------------------------
SERIES = {
    # BRS Des 2019 Tabel 7 (IHK) + tabel rekap BRS Des 2020 (mtm); yoy Des = jangkar BPS 2,72
    2019: dict(
        ihk=[101.61, 101.59, 101.71, 102.07, 102.62, 103.04, 103.36, 103.53, 103.38, 103.43, 103.56, 103.93],
        mtm=[0.32, -0.08, 0.11, 0.44, 0.68, 0.55, 0.31, 0.12, -0.27, 0.02, 0.14, 0.34],
        ytd={12: 2.72},
        yoy=[None] * 11 + [2.72],
    ),
    # Tabel rekap BRS Des 2020 (mtm lengkap); IHK dari BRS Jan/Mei/Ags/Des 2020;
    # yoy: Jan 2,68 (BRS Jan 2020), Mei 2,19 & Sep 1,42 (kutipan BPS), Des 1,68 (BI mengutip BPS)
    2020: dict(
        ihk=[104.33, 104.62, None, None, 104.87, None, 104.95, 104.90, 104.85, None, None, 105.68],
        mtm=[0.39, 0.28, 0.10, 0.08, 0.07, 0.18, -0.10, -0.05, -0.05, 0.07, 0.28, 0.45],
        ytd={12: 1.68},
        yoy=[2.68, None, None, None, 2.19, None, None, None, 1.42, None, None, 1.68],
    ),
    # Hanya jangkar tahunan terverifikasi (BPS): Des 2021 yoy 1,87
    2021: dict(
        ihk=[None] * 12, mtm=[None] * 12, ytd={12: 1.87}, yoy=[None] * 11 + [1.87],
    ),
    # Sep 2022: BRS 3 Okt 2022 (mtm 1,17; yoy 5,95; IHK 112,87).
    # Okt/Nov/Des: BPS Jawa Timur Dalam Angka (IHK + mtm). Des yoy 5,51 (jangkar BPS).
    2022: dict(
        ihk=[None] * 8 + [112.87, 112.75, 112.85, 113.59],
        mtm=[None] * 8 + [1.17, -0.11, 0.09, 0.66],
        ytd={9: 4.84, 12: 5.51},
        yoy=[None] * 8 + [5.95, None, None, 5.51],
    ),
    # Lengkap: BPS Sulawesi Selatan Dalam Angka (mtm) + BRS Gambar 1 (yoy) + IHK BRS berkala.
    # Konsistensi mtm vs IHK terverifikasi 12/12 bulan.
    2023: dict(
        ihk=[113.98, 114.16, 114.36, 114.74, 114.84, 115.00, 115.24, 115.22, 115.44, 115.64, 116.08, 116.56],
        mtm=[0.34, 0.16, 0.18, 0.33, 0.09, 0.14, 0.21, -0.02, 0.19, 0.17, 0.38, 0.41],
        ytd={11: 2.19, 12: 2.61},
        yoy=[5.28, 5.47, 4.97, 4.33, 4.00, 3.52, 3.08, 3.27, 2.28, 2.56, 2.86, 2.61],
    ),
    # Basis baru 2022=100. yoy lengkap dari Gambar 1 BRS; mtm: Jan 0,04 (BRS Jan 2024),
    # Feb/Mar dari Sulsel Dalam Angka, Jul -0,18 (BPS), Sep -0,12 (rantai Tabel 2 BRS).
    2024: dict(
        ihk=[105.19, 105.58, 106.13, None, None, None, 106.09, None, None, None, None, 106.80],
        mtm=[0.04, 0.37, 0.52, None, None, None, -0.18, None, -0.12, None, None, None],
        ytd={7: 0.89, 9: 0.74, 12: 1.57},
        yoy=[2.57, 2.75, 3.05, 3.00, 2.84, 2.51, 2.13, 2.12, 1.84, 1.71, 1.55, 1.57],
    ),
    # yoy lengkap dari Gambar 1 BRS Sep 2026. mtm Feb -0,48 (rantai Tabel 2);
    # Mar 1,65 diturunkan dari IHK terbit Feb 105,48 -> Mar 107,22 (ditandai);
    # Sep 0,21 / Okt 0,28 / Nov 0,17 / Des 0,64 dari BRS bulan terkait.
    # IHK Okt 2025 TIDAK dicantumkan: angka sekunder 109,00 tidak konsisten dengan
    # mtm resmi Okt 0,28% dari IHK Sep 108,74 (implikasinya 109,04) -> dikecualikan.
    2025: dict(
        ihk=[None, 105.48, 107.22, None, None, None, None, None, 108.74, None, 109.22, 109.92],
        mtm=[None, -0.48, 1.65, None, None, None, None, None, 0.21, 0.28, 0.17, 0.64],
        ytd={2: -1.24, 9: 1.82, 10: 2.10, 11: 2.27, 12: 2.92},
        yoy=[0.76, -0.09, 1.03, 1.95, 1.60, 1.87, 2.37, 2.31, 2.65, 2.86, 2.72, 2.92],
    ),
    # Jan mtm -0,15 diturunkan dari IHK terbit Des 2025 109,92 -> Jan 2026 109,75 (ditandai).
    # yoy Mei 3,08 / Jun 3,34 / Jul 2,88 dari posisi label Gambar 1 BRS Sep 2026 (bbox PDF).
    2026: dict(
        ihk=[109.75, 110.50, 110.95, 111.09, None, None, None, 111.97, 112.31] + [None] * 3,
        mtm=[-0.15, 0.68, 0.41, 0.13, None, None, None, None, 0.30] + [None] * 3,
        ytd={2: 0.53, 3: 0.94, 4: 1.06, 9: 2.17},
        yoy=[3.55, 4.76, 3.48, 2.42, 3.08, 3.34, 2.88, 3.19, 3.28] + [None] * 3,
    ),
}

DERIVED = {(2026, 1): "mtm diturunkan dari IHK terbit (109,92 -> 109,75)",
           (2025, 3): "mtm diturunkan dari IHK terbit (105,48 -> 107,22)"}


def write_nasional():
    rows = []
    for yr in sorted(SERIES):
        s = SERIES[yr]
        basis = "2018=100" if yr <= 2023 else "2022=100"
        last = 9 if yr == 2026 else 12
        for m in range(1, last + 1):
            rows.append({
                "tahun": yr, "bulan": m, "nama_bulan": BULAN[m - 1],
                "periode": f"{yr}-{m:02d}",
                "ihk": s["ihk"][m - 1], "basis_ihk": basis if s["ihk"][m - 1] is not None else "",
                "mtm_persen": s["mtm"][m - 1], "ytd_persen": s["ytd"].get(m),
                "yoy_persen": s["yoy"][m - 1],
                "catatan": DERIVED.get((yr, m), ""),
            })
    path = OUT / "inflasi_nasional_bulanan.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


# ----------------------------------------------------------------------------
# KOMPONEN — titik-titik terverifikasi di luar Tabel 9 hasil parse.
# Format: (periode, komponen, mtm, ytd, yoy, andil_mtm, andil_yoy)
# ----------------------------------------------------------------------------
KOMPONEN_EXTRA = [
    ("2020-01", "Inflasi Inti", 0.19, None, 2.88, None, None),
    ("2020-11", "Inflasi Inti", 0.06, None, None, None, None),
    ("2020-11", "Harga Diatur Pemerintah", 0.16, None, None, None, None),
    ("2020-11", "Harga Bergejolak", 1.31, None, None, None, None),
    ("2020-12", "Inflasi Inti", 0.05, None, None, None, None),
    ("2020-12", "Harga Diatur Pemerintah", 0.35, None, None, None, None),
    ("2020-12", "Harga Bergejolak", 2.17, None, None, None, None),
    ("2022-09", "Inflasi Inti", 0.30, 2.81, 3.21, None, None),
    ("2025-09", "Inflasi Inti", 0.18, None, 2.19, None, None),
    ("2025-10", "Inflasi Inti", 0.39, None, 2.36, None, None),
    ("2025-12", "Inflasi Inti", 0.20, None, 2.38, None, 1.53),
    ("2025-12", "Harga Diatur Pemerintah", 0.37, None, 1.93, None, 0.38),
    ("2025-12", "Harga Bergejolak", 2.74, None, None, None, None),
    ("2026-03", "Inflasi Inti", 0.13, 0.93, 2.52, None, None),
    ("2026-04", "Inflasi Inti", 0.23, None, None, 0.15, None),
]

TABEL9_MAP = {"Umum": None, "Inti": "Inflasi Inti",
              "Harga Diatur Pemerintah": "Harga Diatur Pemerintah",
              "Bergejolak": "Harga Bergejolak", "Energi": "Energi",
              "Bahan Makanan": "Bahan Makanan"}


def load_parsed(tag):
    return json.loads((RAW / f"brs_{tag}.json").read_text(encoding="utf-8"))


def write_komponen():
    rows = {}
    for tag, periode in [("2025-11", "2025-11"), ("2026-02", "2026-02"), ("2026-09", "2026-09")]:
        d = load_parsed(tag)
        for r in d["tabel9_komponen"]:
            komp = TABEL9_MAP.get(r["nama"])
            if not komp:
                continue
            v = r["nilai"]  # [ihk_py, ihk_des, ihk, mtm, ytd, yoy, andil_mtm, andil_yoy]
            rows[(periode, komp)] = {
                "periode": periode, "komponen": komp, "ihk": v[2],
                "mtm_persen": v[3], "ytd_persen": v[4], "yoy_persen": v[5],
                "andil_mtm": v[6], "andil_yoy": v[7]}
    for per, komp, mtm, ytd, yoy, am, ay in KOMPONEN_EXTRA:
        key = (per, komp)
        if key not in rows:
            rows[key] = {"periode": per, "komponen": komp, "ihk": None,
                         "mtm_persen": mtm, "ytd_persen": ytd, "yoy_persen": yoy,
                         "andil_mtm": am, "andil_yoy": ay}
    out = sorted(rows.values(), key=lambda r: (r["periode"], r["komponen"]))
    path = OUT / "inflasi_komponen.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    return out


# ----------------------------------------------------------------------------
# KELOMPOK — Tabel 1 hasil parse (3 bulan penuh) + titik terverifikasi lain.
# Format extra: (periode, kelompok, mtm, ytd, yoy, andil_mtm, andil_yoy)
# ----------------------------------------------------------------------------
KELOMPOK_EXTRA = [
    # Sep 2022: mtm per kelompok lengkap (BRS 3 Okt 2022) — bulan kenaikan BBM
    ("2022-09", "Makanan, Minuman, dan Tembakau", -0.30, None, None, None, None),
    ("2022-09", "Pakaian dan Alas Kaki", 0.20, None, None, None, None),
    ("2022-09", "Perumahan, Air, Listrik, dan Bahan Bakar Rumah Tangga", 0.16, None, None, None, None),
    ("2022-09", "Perlengkapan, Peralatan, dan Pemeliharaan Rutin Rumah Tangga", 0.35, None, None, None, None),
    ("2022-09", "Kesehatan", 0.57, None, None, None, None),
    ("2022-09", "Transportasi", 8.88, None, None, None, None),
    ("2022-09", "Informasi, Komunikasi, dan Jasa Keuangan", -0.03, None, None, None, None),
    ("2022-09", "Rekreasi, Olahraga, dan Budaya", 0.31, None, None, None, None),
    ("2022-09", "Pendidikan", 0.21, None, None, None, None),
    ("2022-09", "Penyediaan Makanan dan Minuman/Restoran", 0.57, None, None, None, None),
    ("2022-09", "Perawatan Pribadi dan Jasa Lainnya", 0.28, None, None, None, None),
    # Des 2023: kelompok makanan yoy + andil terbesar (konferensi pers BPS)
    ("2023-12", "Makanan, Minuman, dan Tembakau", None, None, 6.18, None, 1.60),
    # Des 2025: makanan yoy 4,58 andil 1,33 (terbesar); Informasi andil yoy -0,02 (deflasi)
    ("2025-12", "Makanan, Minuman, dan Tembakau", None, None, 4.58, None, 1.33),
    ("2025-12", "Informasi, Komunikasi, dan Jasa Keuangan", None, None, None, None, -0.02),
    # Mar 2026: tiga kelompok teratas yoy (BRS Mar 2026 via kutipan BPS)
    ("2026-03", "Perumahan, Air, Listrik, dan Bahan Bakar Rumah Tangga", None, None, 7.24, None, 1.08),
    ("2026-03", "Perawatan Pribadi dan Jasa Lainnya", None, None, 15.32, None, 1.02),
    ("2026-03", "Makanan, Minuman, dan Tembakau", None, None, 3.34, None, 0.99),
    # Apr 2026: mtm transportasi & makanan (BRS Apr 2026)
    ("2026-04", "Transportasi", 0.99, None, None, 0.12, None),
    ("2026-04", "Makanan, Minuman, dan Tembakau", -0.20, None, None, -0.06, None),
]


KELOMPOK_FIX = {"Makanan, Minuman dan Tembakau": "Makanan, Minuman, dan Tembakau"}


def write_kelompok():
    rows = {}
    for tag, periode in [("2025-11", "2025-11"), ("2026-02", "2026-02"), ("2026-09", "2026-09")]:
        d = load_parsed(tag)
        for r in d["tabel1_kelompok"]:
            if r["nama"] == "Umum":
                continue
            v = r["nilai"]
            nama = KELOMPOK_FIX.get(r["nama"], r["nama"])
            rows[(periode, nama)] = {
                "periode": periode, "kelompok": nama, "ihk": v[2],
                "mtm_persen": v[3], "ytd_persen": v[4], "yoy_persen": v[5],
                "andil_mtm": v[6], "andil_yoy": v[7]}
    for per, kel, mtm, ytd, yoy, am, ay in KELOMPOK_EXTRA:
        key = (per, kel)
        if key not in rows:
            rows[key] = {"periode": per, "kelompok": kel, "ihk": None,
                         "mtm_persen": mtm, "ytd_persen": ytd, "yoy_persen": yoy,
                         "andil_mtm": am, "andil_yoy": ay}
    out = sorted(rows.values(), key=lambda r: (r["periode"], r["kelompok"]))
    path = OUT / "inflasi_kelompok.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    return out


def write_geo():
    d = load_parsed("2026-09")
    prov = sorted(d["provinsi"], key=lambda x: x["no"])
    kota = sorted(d["kota"], key=lambda x: -x["yoy"])
    with open(OUT / "inflasi_provinsi_2026_09.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["provinsi", "ihk", "yoy_persen", "mtm_persen"])
        w.writeheader()
        for r in prov:
            w.writerow({"provinsi": r["nama"], "ihk": r["ihk"],
                        "yoy_persen": r["yoy"], "mtm_persen": r["mtm"]})
    with open(OUT / "inflasi_kota_2026_09.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kabupaten_kota", "ihk", "yoy_persen", "mtm_persen"])
        w.writeheader()
        for r in kota:
            w.writerow({"kabupaten_kota": r["nama"], "ihk": r["ihk"],
                        "yoy_persen": r["yoy"], "mtm_persen": r["mtm"]})
    return prov, kota


def main():
    nas = write_nasional()
    kom = write_komponen()
    kel = write_kelompok()
    prov, kota = write_geo()
    yoy_pts = sum(1 for r in nas if r["yoy_persen"] is not None)
    mtm_pts = sum(1 for r in nas if r["mtm_persen"] is not None)
    print(f"nasional: {len(nas)} baris bulan | yoy terisi {yoy_pts} | mtm terisi {mtm_pts}")
    print(f"komponen: {len(kom)} baris | kelompok: {len(kel)} baris")
    print(f"provinsi Sep 2026: {len(prov)} | kota Sep 2026: {len(kota)}")
    # --- Verifikasi jangkar Desember (yoy) ---
    anchors = {2019: 2.72, 2020: 1.68, 2021: 1.87, 2022: 5.51, 2023: 2.61, 2024: 1.57, 2025: 2.92}
    ok = True
    for yr, exp in anchors.items():
        got = SERIES[yr]["yoy"][11]
        status = "OK" if got == exp else f"SELISIH (data {got})"
        if got != exp:
            ok = False
        print(f"  Jangkar Des {yr}: target {exp} -> {status}")
    peak = max((r["yoy_persen"], r["periode"]) for r in nas if r["yoy_persen"] is not None)
    print(f"  Puncak yoy pada seri terkumpul: {peak[0]}% pada {peak[1]} (era 2022: Sep 2022 = 5,95%)")
    print("  Semua jangkar cocok." if ok else "  ADA SELISIH JANGKAR — periksa!")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Membangun kit Power BI untuk proyek Inflasi Indonesia 2026:
CSV model bintang (grain terpisah per fakta), measures_dax.md (nama measure
polos + tabel verifikasi yang dihitung dari fakta yang sama),
dashboard_layout.md, build_guide.md, dashboard_preview_halaman1.png.
Angka preview dibaca kembali dari fact CSV yang baru ditulis.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")
PBI = os.path.join(ROOT, "powerbi")
os.makedirs(PBI, exist_ok=True)

NAVY = "#14406B"; RED = "#D62828"; BUTTER = "#F2C14E"; TEAL = "#2A9D8F"
SLATE = "#26313B"; GREY = "#7A8794"; OAT = "#FAF6EF"; LIGHT = "#EAF0F7"
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def fmt_id(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


nas = pd.read_csv(os.path.join(DATA, "inflasi_nasional_bulanan.csv"))
kom = pd.read_csv(os.path.join(DATA, "inflasi_komponen.csv"))
kel = pd.read_csv(os.path.join(DATA, "inflasi_kelompok.csv"))
kota = pd.read_csv(os.path.join(DATA, "inflasi_kota_2026_09.csv"))
prov = pd.read_csv(os.path.join(DATA, "inflasi_provinsi_2026_09.csv"))

# ------------------------------------------------------------------ dimensi
dim_bulan = pd.DataFrame({
    "bulan_key": [int(p.replace("-", "")) for p in nas["periode"]],
    "periode": nas["periode"],
    "tahun": nas["tahun"].astype(int),
    "bulan": nas["bulan"].astype(int),
    "nama_bulan": nas["nama_bulan"],
    "label": [f"{b[:3]} {t}" for b, t in zip(nas["nama_bulan"], nas["tahun"])],
})
dim_bulan.to_csv(os.path.join(PBI, "dim_bulan.csv"), index=False)

dim_tahun = pd.DataFrame({"tahun_id": sorted(nas["tahun"].unique().astype(int)),
                          "tahun": sorted(nas["tahun"].unique().astype(int))})
dim_tahun.to_csv(os.path.join(PBI, "dim_tahun.csv"), index=False)

kel_order = list(dict.fromkeys(kel["kelompok"].tolist()))
KID = {k: i + 1 for i, k in enumerate(kel_order)}
pd.DataFrame({"kelompok_id": range(1, len(kel_order) + 1), "kelompok": kel_order}).to_csv(
    os.path.join(PBI, "dim_kelompok.csv"), index=False)

kota_order = list(kota["kabupaten_kota"])
pd.DataFrame({"kota_id": range(1, len(kota_order) + 1), "kabupaten_kota": kota_order}).to_csv(
    os.path.join(PBI, "dim_kota.csv"), index=False)

prov_order = list(prov["provinsi"])
pd.DataFrame({"provinsi_id": range(1, len(prov_order) + 1), "provinsi": prov_order}).to_csv(
    os.path.join(PBI, "dim_provinsi.csv"), index=False)

# ------------------------------------------------------------------ fakta
fact_bulanan = pd.DataFrame({
    "bulan_key": [int(p.replace("-", "")) for p in nas["periode"]],
    "tahun_id": nas["tahun"].astype(int),
    "ihk": nas["ihk"], "mtm_persen": nas["mtm_persen"],
    "ytd_persen": nas["ytd_persen"], "yoy_persen": nas["yoy_persen"],
})
fact_bulanan.to_csv(os.path.join(PBI, "fact_inflasi_bulanan.csv"), index=False)

fact_kelompok = pd.DataFrame({
    "bulan_key": [int(p.replace("-", "")) for p in kel["periode"]],
    "kelompok_id": [KID[k] for k in kel["kelompok"]],
    "ihk": kel["ihk"], "mtm_persen": kel["mtm_persen"], "ytd_persen": kel["ytd_persen"],
    "yoy_persen": kel["yoy_persen"], "andil_mtm": kel["andil_mtm"], "andil_yoy": kel["andil_yoy"],
})
fact_kelompok.to_csv(os.path.join(PBI, "fact_inflasi_kelompok.csv"), index=False)

kom_order = list(dict.fromkeys(kom["komponen"].tolist()))
KOMID = {k: i + 1 for i, k in enumerate(kom_order)}
pd.DataFrame({"komponen_id": range(1, len(kom_order) + 1), "komponen": kom_order}).to_csv(
    os.path.join(PBI, "dim_komponen.csv"), index=False)
fact_komponen = pd.DataFrame({
    "bulan_key": [int(p.replace("-", "")) for p in kom["periode"]],
    "komponen_id": [KOMID[k] for k in kom["komponen"]],
    "ihk": kom["ihk"], "mtm_persen": kom["mtm_persen"], "ytd_persen": kom["ytd_persen"],
    "yoy_persen": kom["yoy_persen"], "andil_mtm": kom["andil_mtm"], "andil_yoy": kom["andil_yoy"],
})
fact_komponen.to_csv(os.path.join(PBI, "fact_inflasi_komponen.csv"), index=False)

fact_kota = pd.DataFrame({
    "kota_id": range(1, len(kota) + 1), "bulan_key": 202609,
    "ihk": kota["ihk"], "yoy_persen": kota["yoy_persen"], "mtm_persen": kota["mtm_persen"],
})
fact_kota.to_csv(os.path.join(PBI, "fact_inflasi_kota.csv"), index=False)

fact_prov = pd.DataFrame({
    "provinsi_id": range(1, len(prov) + 1), "bulan_key": 202609,
    "ihk": prov["ihk"], "yoy_persen": prov["yoy_persen"], "mtm_persen": prov["mtm_persen"],
})
fact_prov.to_csv(os.path.join(PBI, "fact_inflasi_provinsi.csv"), index=False)

# ------------------------------------------------------------------ verifikasi (dari fakta)
fb = pd.read_csv(os.path.join(PBI, "fact_inflasi_bulanan.csv"))
fk = pd.read_csv(os.path.join(PBI, "fact_inflasi_kota.csv"))
fkel = pd.read_csv(os.path.join(PBI, "fact_inflasi_kelompok.csv"))
last = fb[fb["bulan_key"] == 202609].iloc[0]
VER = {
    "Inflasi YoY Terbaru (Sep 2026)": (float(last["yoy_persen"]), "fact_inflasi_bulanan, bulan_key 202609"),
    "Inflasi MtM Terbaru (Sep 2026)": (float(last["mtm_persen"]), "fact_inflasi_bulanan, bulan_key 202609"),
    "IHK Terbaru (Sep 2026, 2022=100)": (float(last["ihk"]), "fact_inflasi_bulanan, bulan_key 202609"),
    "Inflasi YoY Tertinggi pada seri": (float(fb["yoy_persen"].max()), "MAX fact_inflasi_bulanan (Sep 2022)"),
    "Jumlah Bulan Deflasi (mtm terisi)": (int((fb["mtm_persen"] < 0).sum()), "COUNT fact_inflasi_bulanan mtm < 0"),
    "Kota YoY Tertinggi (Sep 2026)": (float(fk["yoy_persen"].max()), "MAX fact_inflasi_kota (Kab. Minahasa Utara)"),
    "Kota YoY Terendah (Sep 2026)": (float(fk["yoy_persen"].min()), "MIN fact_inflasi_kota (Kab. Timor Tengah Selatan)"),
    "Kota di Atas YoY Nasional": (int((fk["yoy_persen"] > float(last["yoy_persen"])).sum()), "COUNT fact_inflasi_kota yoy > 3,28"),
    "Andil YoY Kelompok Terbesar (Sep 2026)": (
        float(fkel[fkel["bulan_key"] == 202609]["andil_yoy"].max()), "MAX fact_inflasi_kelompok (Makanan)"),
}

ver_rows = "\n".join(
    f"| {k} | {fmt_id(v) if isinstance(v, float) else v} | {src} |" for k, (v, src) in VER.items())

MEASURES_MD = f"""# Measure DAX: Inflasi Indonesia 2026

Model bintang: `fact_inflasi_bulanan` (93 bulan), `fact_inflasi_kelompok`,
`fact_inflasi_komponen`, `fact_inflasi_kota` (150 kab/kota, Sep 2026), dan
`fact_inflasi_provinsi` (38 provinsi, Sep 2026) — setiap fakta pada grain-nya
sendiri, terhubung ke `dim_bulan`, `dim_tahun`, `dim_kelompok`, `dim_komponen`,
`dim_kota`, dan `dim_provinsi`. Semua relasi difilter satu arah (Single).

Nama measure polos (tanpa tanda sama dengan di dalam nama). Tempel satu
measure per kotak formula.

```dax
Inflasi YoY =
AVERAGE ( fact_inflasi_bulanan[yoy_persen] )

Inflasi MtM =
AVERAGE ( fact_inflasi_bulanan[mtm_persen] )

IHK =
AVERAGE ( fact_inflasi_bulanan[ihk] )

Inflasi YoY Terbaru =
VAR KunciTerbaru =
    MAX ( fact_inflasi_bulanan[bulan_key] )
RETURN
    CALCULATE ( [Inflasi YoY], fact_inflasi_bulanan[bulan_key] = KunciTerbaru )

Puncak Inflasi YoY =
MAX ( fact_inflasi_bulanan[yoy_persen] )

Jumlah Bulan Deflasi =
CALCULATE (
    COUNTROWS ( fact_inflasi_bulanan ),
    fact_inflasi_bulanan[mtm_persen] < 0
)

Andil YoY Kelompok =
AVERAGE ( fact_inflasi_kelompok[andil_yoy] )

Andil YoY Komponen =
AVERAGE ( fact_inflasi_komponen[andil_yoy] )

Kota YoY Tertinggi =
MAX ( fact_inflasi_kota[yoy_persen] )

Kota YoY Terendah =
MIN ( fact_inflasi_kota[yoy_persen] )

Jumlah Kota Di Atas Nasional =
VAR Nasional = [Inflasi YoY Terbaru]
RETURN
    CALCULATE (
        COUNTROWS ( fact_inflasi_kota ),
        fact_inflasi_kota[yoy_persen] > Nasional
    )

Provinsi YoY Tertinggi =
MAX ( fact_inflasi_provinsi[yoy_persen] )
```

Format tampilan: YoY, MtM, Puncak, Andil sebagai Number 2 desimal dengan
akhiran persen pada visual (nilai sudah dalam satuan persen, bukan rasio);
IHK sebagai Number 2 desimal; jumlah sebagai Whole number.

## Tabel verifikasi (dihitung dari fact CSV yang sama)

| Measure | Nilai yang harus tampil | Sumber perhitungan |
|---|---|---|
{ver_rows}
"""

with open(os.path.join(PBI, "measures_dax.md"), "w", encoding="utf-8") as f:
    f.write(MEASURES_MD)

LAYOUT_MD = """# Layout Dashboard Power BI: Inflasi Indonesia 2026

Nama berkas: `Inflasi-Indonesia-2026.pbix`. Tema: navy `#14406B`, merah
`#D62828`, kuning mentega `#F2C14E`, teal `#2A9D8F`, latar oat `#FAF6EF`.
Setiap halaman memakai slicer Periode (dim_bulan) bila relevan.

## Halaman 1 — Ringkasan Inflasi
- 4 kartu KPI: Inflasi YoY Terbaru (3,28%), Inflasi MtM Terbaru (0,30%),
  IHK Terbaru (112,31; basis 2022=100), Puncak Inflasi YoY (5,95%).
- Line chart: Inflasi YoY Jan 2023 – Sep 2026 dengan pita sasaran BI
  1,5%–3,5% (constant line 1,5 dan 3,5).
- Bar chart: andil yoy per kelompok Sep 2026 (Makanan terbesar 1,28 poin).
- Teks insight: 19 dari 24 bulan terakhir berada di dalam sasaran BI.

## Halaman 2 — Komponen dan Kelompok
- Bar chart: yoy per komponen Sep 2026 (Bergejolak 5,03; Diatur 3,25; Inti 2,84).
- Bar chart: andil yoy per komponen (Inti 1,82 terbesar).
- Clustered bar: yoy 11 kelompok pengeluaran Sep 2026.
- Tabel: kelompok pada Nov 2025, Feb 2026, Sep 2026 (mtm, yoy, andil).

## Halaman 3 — Peta Harga per Wilayah
- Bar chart: 38 provinsi Sep 2026 terurut (Sulawesi Utara 7,59% tertinggi).
- Bar chart: 10 kab/kota tertinggi dan 10 terendah (Minahasa Utara 9,05%;
  Timor Tengah Selatan 1,04%).
- Kartu: 92 dari 150 kab/kota di atas inflasi nasional; rentang 8,01 poin.
- Histogram/distribusi yoy kab/kota bila visual tersedia.

## Halaman 4 — Sejarah dan Kemusiman
- Bar chart mtm 2019–2026 (deflasi ditandai merah; celah = tidak terkompilasi).
- Bar chart: inflasi tahunan Desember 2019–2025 (2022 tertinggi 5,51%).
- Bar chart: rata-rata mtm per bulan kalender (puncak Maret dan Desember).
- Bar chart kelompok mtm Sep 2022: Transportasi +8,88% pada bulan kenaikan BBM.
"""

with open(os.path.join(PBI, "dashboard_layout.md"), "w", encoding="utf-8") as f:
    f.write(LAYOUT_MD)

GUIDE_MD = """# Panduan Merakit Dashboard: Inflasi Indonesia 2026

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
"""

with open(os.path.join(PBI, "build_guide.md"), "w", encoding="utf-8") as f:
    f.write(GUIDE_MD)

# ------------------------------------------------------------------ preview hal. 1
fb2 = fb.sort_values("bulan_key")
tren = fb2[(fb2["bulan_key"] >= 202301)].dropna(subset=["yoy_persen"])
kel9 = fkel[fkel["bulan_key"] == 202609].merge(
    pd.read_csv(os.path.join(PBI, "dim_kelompok.csv")), on="kelompok_id").dropna(subset=["andil_yoy"])
kel9 = kel9.sort_values("andil_yoy")

fig = plt.figure(figsize=(13.33, 7.5))
fig.patch.set_facecolor(OAT)
ax_bg = fig.add_axes([0, 0, 1, 1]); ax_bg.axis("off")
ax_bg.add_patch(plt.Rectangle((0, 0.86), 1, 0.14, color=NAVY, transform=ax_bg.transAxes))
ax_bg.text(0.03, 0.955, "INFLASI INDONESIA 2026", color="white", fontsize=21,
           fontweight="bold", transform=ax_bg.transAxes, va="center")
ax_bg.text(0.03, 0.895, "Halaman 1 - Ringkasan Inflasi  |  Sumber: BPS (BRS Perkembangan IHK)",
           color=BUTTER, fontsize=11.5, transform=ax_bg.transAxes, va="center")

kpis = [
    ("Inflasi YoY Sep 2026", fmt_id(float(last["yoy_persen"])) + "%", NAVY),
    ("Inflasi MtM Sep 2026", fmt_id(float(last["mtm_persen"])) + "%", TEAL),
    ("IHK Sep 2026 (2022=100)", fmt_id(float(last["ihk"])), SLATE),
    ("Puncak YoY (Sep 2022)", fmt_id(float(fb["yoy_persen"].max())) + "%", RED),
]
for i, (lab, val, c) in enumerate(kpis):
    x = 0.03 + i * 0.245
    ax_bg.add_patch(plt.Rectangle((x, 0.70), 0.225, 0.13, facecolor="white",
                                  edgecolor=c, lw=1.6, transform=ax_bg.transAxes))
    ax_bg.text(x + 0.012, 0.805, lab, fontsize=10, color=GREY, transform=ax_bg.transAxes)
    ax_bg.text(x + 0.012, 0.735, val, fontsize=21, fontweight="bold", color=c,
               transform=ax_bg.transAxes)

ax1 = fig.add_axes([0.045, 0.10, 0.55, 0.52])
tgl = pd.to_datetime(tren["bulan_key"].astype(str), format="%Y%m")
ax1.axhspan(1.5, 3.5, color=BUTTER, alpha=0.35)
ax1.plot(tgl, tren["yoy_persen"], color=NAVY, lw=2)
ax1.fill_between(tgl, tren["yoy_persen"], color=NAVY, alpha=0.08)
ax1.set_title("Tren Inflasi YoY (pita kuning = sasaran BI 1,5%–3,5%)", fontsize=11.5, color=NAVY, fontweight="bold")
ax1.set_ylabel("%"); ax1.grid(axis="y", alpha=0.25)

ax2 = fig.add_axes([0.65, 0.10, 0.325, 0.52])
short = [k.replace("Makanan, Minuman, dan Tembakau", "Makanan & Tembakau")
         .replace("Perawatan Pribadi dan Jasa Lainnya", "Perawatan Pribadi")
         .replace("Perlengkapan, Peralatan, dan Pemeliharaan Rutin Rumah Tangga", "Perlengkapan RT")
         .replace("Perumahan, Air, Listrik, dan Bahan Bakar Rumah Tangga", "Perumahan & Listrik")
         .replace("Informasi, Komunikasi, dan Jasa Keuangan", "Info & Keuangan")
         .replace("Penyediaan Makanan dan Minuman/Restoran", "Restoran") for k in kel9["kelompok"]]
ax2.barh(short, kel9["andil_yoy"], color=TEAL, height=0.62)
ax2.set_title("Andil YoY per Kelompok, Sep 2026 (poin %)", fontsize=11.5, color=NAVY, fontweight="bold")
ax2.tick_params(labelsize=8)
fig.savefig(os.path.join(PBI, "dashboard_preview_halaman1.png"), dpi=150, facecolor=OAT)
plt.close(fig)
print("Kit Power BI selesai. Verifikasi:")
for k, (v, s) in VER.items():
    print(" -", k, "=", v)

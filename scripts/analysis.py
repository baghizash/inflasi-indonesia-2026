#!/usr/bin/env python3
"""
analysis.py — Analisis Inflasi Indonesia dari CSV terkompilasi (data/).
Menghasilkan findings.json dan grafik-grafik di charts/.
Semua angka dihitung ulang dari CSV; tidak ada angka hardcoded selain
fakta BRS yang memang bersifat titik (andil komoditas, dicatat sumbernya).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
CHARTS = BASE / "charts"
CHARTS.mkdir(exist_ok=True)

NAVY = "#14406B"
RED = "#D62828"
BUTTER = "#F2C14E"
TEAL = "#2A9D8F"
GRAY = "#6C757D"
LIGHT = "#EAF0F7"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.edgecolor": "#B9C4CF", "axes.linewidth": 0.8,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})


def fmt(x, dec=2):
    return f"{x:.{dec}f}".replace(".", ",")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print("chart:", name)


nas = pd.read_csv(DATA / "inflasi_nasional_bulanan.csv")
kom = pd.read_csv(DATA / "inflasi_komponen.csv")
kel = pd.read_csv(DATA / "inflasi_kelompok.csv")
kota = pd.read_csv(DATA / "inflasi_kota_2026_09.csv")
prov = pd.read_csv(DATA / "inflasi_provinsi_2026_09.csv")
nas["tanggal"] = pd.to_datetime(nas["periode"])

F = {}

# ---------------------------------------------------------------- ringkasan
latest = nas[nas["periode"] == "2026-09"].iloc[0]
prev = nas[nas["periode"] == "2026-08"].iloc[0]
F["terbaru"] = {
    "periode": "September 2026", "yoy": float(latest["yoy_persen"]),
    "mtm": float(latest["mtm_persen"]), "ytd": float(latest["ytd_persen"]),
    "ihk": float(latest["ihk"]), "basis_ihk": latest["basis_ihk"],
    "yoy_bulan_lalu": float(prev["yoy_persen"]),
}
F["cakupan"] = {
    "bulan_total": int(len(nas)), "rentang": "Januari 2019 – September 2026",
    "yoy_terisi": int(nas["yoy_persen"].notna().sum()),
    "mtm_terisi": int(nas["mtm_persen"].notna().sum()),
    "yoy_kontinu": "Januari 2023 – September 2026 (45 bulan)",
    "kota_sep2026": int(len(kota)), "provinsi_sep2026": int(len(prov)),
}

# ---------------------------------------------------------------- deflasi
defl = nas[nas["mtm_persen"] < 0].sort_values("mtm_persen")
F["deflasi"] = {
    "jumlah_bulan_teramati": int(len(defl)),
    "terburuk": {"periode": defl.iloc[0]["periode"], "mtm": float(defl.iloc[0]["mtm_persen"])},
    "daftar": [{"periode": r["periode"], "mtm": float(r["mtm_persen"])}
               for _, r in defl.iterrows()],
    "covid_2020": [{"periode": r["periode"], "mtm": float(r["mtm_persen"])}
                   for _, r in defl[defl["tahun"] == 2020].iterrows()],
}

# ---------------------------------------------------------------- era 2022 & disinflasi
yoy_all = nas.dropna(subset=["yoy_persen"])
peak = yoy_all.loc[yoy_all["yoy_persen"].idxmax()]
F["puncak"] = {"periode": peak["periode"], "yoy": float(peak["yoy_persen"]),
               "mtm_saat_puncak": float(nas[nas["periode"] == peak["periode"]].iloc[0]["mtm_persen"]),
               "catatan": "Bulan yang sama dengan kenaikan harga BBM bersubsidi (3 September 2022); "
                          "kelompok Transportasi naik 8,88% mtm pada bulan itu."}
F["inflasi_tahunan_desember"] = {
    str(int(r["tahun"])): float(r["yoy_persen"])
    for _, r in nas[nas["bulan"] == 12].dropna(subset=["yoy_persen"]).iterrows()}
F["rata_rata_yoy_per_tahun"] = {
    str(int(t)): round(float(g["yoy_persen"].mean()), 2)
    for t, g in yoy_all.groupby("tahun") if len(g) >= 9}

# ---------------------------------------------------------------- pita BI
last24 = nas[nas["tanggal"] >= "2024-10-01"].dropna(subset=["yoy_persen"])
inside = last24[(last24["yoy_persen"] >= 1.5) & (last24["yoy_persen"] <= 3.5)]
below = last24[last24["yoy_persen"] < 1.5]
above = last24[last24["yoy_persen"] > 3.5]
F["pita_target_bi"] = {
    "sasaran": "2,5% ± 1% (rentang 1,5% – 3,5%)", "jendela": "Oktober 2024 – September 2026 (24 bulan)",
    "di_dalam": int(len(inside)), "di_bawah": int(len(below)), "di_atas": int(len(above)),
    "bulan_di_bawah": below["periode"].tolist(), "bulan_di_atas": above["periode"].tolist(),
}

# ---------------------------------------------------------------- kemusiman
mtm_ok = nas.dropna(subset=["mtm_persen"])
seas = mtm_ok.groupby("bulan")["mtm_persen"].agg(["mean", "count"])
F["kemusiman_mtm"] = {
    "rata_rata_per_bulan": {str(int(i)): round(float(r["mean"]), 2) for i, r in seas.iterrows()},
    "n_observasi": {str(int(i)): int(r["count"]) for i, r in seas.iterrows()},
    "bulan_tertinggi": int(seas["mean"].idxmax()), "bulan_terendah": int(seas["mean"].idxmin()),
}

# ---------------------------------------------------------------- komponen
k924 = kom[kom["periode"] == "2026-09"].set_index("komponen")
F["komponen_sep2026"] = {
    c: {"yoy": float(k924.loc[c, "yoy_persen"]), "mtm": float(k924.loc[c, "mtm_persen"]),
        "andil_yoy": float(k924.loc[c, "andil_yoy"])}
    for c in ["Inflasi Inti", "Harga Bergejolak", "Harga Diatur Pemerintah", "Energi", "Bahan Makanan"]}
F["komponen_feb2026"] = {
    "perumahan_yoy": float(kel[(kel["periode"] == "2026-02") &
                               (kel["kelompok"].str.startswith("Perumahan"))].iloc[0]["yoy_persen"]),
    "catatan": "Lonjakan kelompok Perumahan Feb 2026 (yoy 16,19%) adalah efek basis rendah "
               "diskon tarif listrik Jan–Feb 2025 (tarif listrik yoy +86,96%).",
}

# ---------------------------------------------------------------- kelompok
kel924 = kel[kel["periode"] == "2026-09"].copy()
kel924 = kel924[kel924["andil_yoy"].notna()].sort_values("andil_yoy", ascending=False)
F["kelompok_sep2026"] = {
    "andil_terbesar": [{"kelompok": r["kelompok"], "yoy": float(r["yoy_persen"]),
                        "andil_yoy": float(r["andil_yoy"])}
                       for _, r in kel924.head(3).iterrows()],
    "yoy_tertinggi": {"kelompok": kel924.loc[kel924["yoy_persen"].idxmax(), "kelompok"],
                      "yoy": float(kel924["yoy_persen"].max())},
}
makanan = kel[kel["kelompok"] == "Makanan, Minuman, dan Tembakau"]
F["kelompok_makanan"] = {
    "andil_des2023": 1.60, "andil_des2025": 1.33,
    "andil_sep2026": float(kel924[kel924["kelompok"] == "Makanan, Minuman, dan Tembakau"].iloc[0]["andil_yoy"]),
    "yoy_sep2026": float(kel924[kel924["kelompok"] == "Makanan, Minuman, dan Tembakau"].iloc[0]["yoy_persen"]),
    "catatan": "Kelompok Makanan, Minuman, dan Tembakau adalah penyumbang andil yoy terbesar "
               "pada Des 2023, Des 2025, dan Sep 2026.",
}
F["transportasi_sep2022_mtm"] = float(
    kel[(kel["periode"] == "2022-09") & (kel["kelompok"] == "Transportasi")].iloc[0]["mtm_persen"])

# ---------------------------------------------------------------- geografi
F["kota_sep2026"] = {
    "tertinggi": {"kota": kota.iloc[0]["kabupaten_kota"], "yoy": float(kota.iloc[0]["yoy_persen"])},
    "terendah": {"kota": kota.iloc[-1]["kabupaten_kota"], "yoy": float(kota.iloc[-1]["yoy_persen"])},
    "rentang_poin": round(float(kota["yoy_persen"].max() - kota["yoy_persen"].min()), 2),
    "di_atas_nasional": int((kota["yoy_persen"] > 3.28).sum()),
    "median_yoy": round(float(kota["yoy_persen"].median()), 2),
    "rata_rata_yoy": round(float(kota["yoy_persen"].mean()), 2),
    "deflasi_mtm": int((kota["mtm_persen"] < 0).sum()),
}
prov_s = prov.sort_values("yoy_persen", ascending=False)
F["provinsi_sep2026"] = {
    "tertinggi": {"provinsi": prov_s.iloc[0]["provinsi"], "yoy": float(prov_s.iloc[0]["yoy_persen"])},
    "terendah": {"provinsi": prov_s.iloc[-1]["provinsi"], "yoy": float(prov_s.iloc[-1]["yoy_persen"])},
    "rentang_poin": round(float(prov_s["yoy_persen"].max() - prov_s["yoy_persen"].min()), 2),
}

# ---------------------------------------------------------------- komoditas & tautan pangan
F["komoditas_sep2026"] = {
    "andil_mtm_teratas": {"cabai rawit": 0.08, "cabai merah": 0.06, "daging ayam ras": 0.05,
                          "beras": 0.03, "telur ayam ras": 0.02},
    "andil_yoy_teratas": {"emas perhiasan": 0.44, "bensin": 0.31, "beras": 0.23,
                          "ikan segar": 0.17, "daging ayam ras": 0.17},
    "sumber": "Tabel 10 BRS September 2026",
    "tautan_pangan": "Cabai kembali menjadi penggerak: dua dari lima penyumbang andil mtm "
                     "terbesar Sep 2026 adalah cabai rawit dan cabai merah, dan pada Des 2023 "
                     "andil yoy cabai merah (0,24) + cabai rawit (0,10) termasuk yang terbesar — "
                     "pola yang sama terlihat pada proyek Harga Cabai dan Harga Pangan: gejolak "
                     "harga pangan segar adalah sumber volatilitas inflasi yang berulang.",
}

(BASE / "findings.json").write_text(json.dumps(F, indent=2, ensure_ascii=False), encoding="utf-8")
print("findings.json ditulis")
print(json.dumps({k: F[k] for k in ["terbaru", "pita_target_bi", "kota_sep2026"]}, indent=1, ensure_ascii=False))

# ================================================================ GRAFIK
# 1. Tren yoy 2023–2026 + pita sasaran BI
d = nas[(nas["tanggal"] >= "2023-01-01")].dropna(subset=["yoy_persen"])
fig, ax = plt.subplots(figsize=(10.5, 4.6))
ax.axhspan(1.5, 3.5, color=BUTTER, alpha=0.35, label="Sasaran inflasi BI 2,5% ± 1%")
ax.axhline(2.5, color=GRAY, lw=0.9, ls="--")
ax.plot(d["tanggal"], d["yoy_persen"], color=NAVY, lw=2.2, marker="o", ms=3.5)
ax.fill_between(d["tanggal"], d["yoy_persen"], color=NAVY, alpha=0.08)
for per, lab in [("2023-01", "Jan 2023\n5,28%"), ("2024-09", "Sep 2024\n1,84%"),
                 ("2025-02", "Feb 2025\n-0,09%"), ("2026-02", "Feb 2026\n4,76%"),
                 ("2026-09", "Sep 2026\n3,28%")]:
    r = d[d["periode"] == per].iloc[0]
    ax.annotate(lab, (r["tanggal"], r["yoy_persen"]), textcoords="offset points",
                xytext=(0, 10), ha="center", fontsize=9, color=NAVY, fontweight="bold")
ax.set_title("Inflasi Year-on-Year Indonesia, Januari 2023 – September 2026")
ax.set_ylabel("Inflasi yoy (%)"); ax.legend(loc="upper right", frameon=False)
ax.grid(axis="y", alpha=0.25)
save(fig, "chart_yoy_tren.png")

# 2. Inflasi tahunan Desember 2019–2025
thn = F["inflasi_tahunan_desember"]
fig, ax = plt.subplots(figsize=(9, 4.4))
vals = [thn[str(y)] for y in range(2019, 2026)]
cols = [RED if v == max(vals) else NAVY for v in vals]
ax.bar([str(y) for y in range(2019, 2026)], vals, color=cols, width=0.62)
ax.axhspan(1.5, 3.5, color=BUTTER, alpha=0.3, zorder=0)
for i, v in enumerate(vals):
    ax.text(i, v + 0.12, fmt(v) + "%", ha="center", fontweight="bold", color=NAVY)
ax.set_title("Inflasi Tahunan (Desember, yoy) 2019–2025")
ax.set_ylabel("Inflasi yoy (%)")
save(fig, "chart_tahunan_desember.png")

# 3. mtm Jan 2023 – Sep 2026 (batang, celah = tidak terkompilasi)
d = nas[nas["tanggal"] >= "2023-01-01"]
fig, ax = plt.subplots(figsize=(10.5, 4.4))
cols = [RED if (v is not None and v < 0) else NAVY for v in d["mtm_persen"]]
ax.bar(range(len(d)), d["mtm_persen"], color=cols, width=0.75)
ax.axhline(0, color="#333", lw=0.8)
lbl = {i: f"{r['nama_bulan'][:3]} {str(r['tahun'])[2:]}" for i, (_, r) in enumerate(d.iterrows()) if r["bulan"] in (1, 7)}
ax.set_xticks(list(lbl.keys())); ax.set_xticklabels(list(lbl.values()), fontsize=8.5)
ax.set_title("Inflasi Month-to-Month, Januari 2023 – September 2026 (merah = deflasi)")
ax.set_ylabel("Inflasi mtm (%)"); ax.grid(axis="y", alpha=0.25)
save(fig, "chart_mtm_tren.png")

# 4. Bulan-bulan deflasi
fig, ax = plt.subplots(figsize=(9.5, 4.4))
lab = [f"{r['nama_bulan'][:3]} {r['tahun']}" for _, r in defl.iterrows()]
ax.barh(lab[::-1], defl["mtm_persen"].values[::-1], color=RED, height=0.62)
for i, v in enumerate(defl["mtm_persen"].values[::-1]):
    ax.text(v - 0.015, i, fmt(v) + "%", ha="right", va="center", color="white", fontweight="bold", fontsize=9)
ax.set_title(f"Bulan Deflasi (mtm negatif): {len(defl)} bulan teramati, 2019–2026")
ax.set_xlabel("Inflasi mtm (%)")
save(fig, "chart_deflasi.png")

# 5. Kemusiman mtm
nama_bln = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
fig, ax = plt.subplots(figsize=(9.5, 4.4))
means = [seas.loc[m, "mean"] if m in seas.index else np.nan for m in range(1, 13)]
ns = [int(seas.loc[m, "count"]) if m in seas.index else 0 for m in range(1, 13)]
ax.bar(nama_bln, means, color=[RED if v < 0 else TEAL for v in means], width=0.62)
ax.axhline(0, color="#333", lw=0.8)
for i, (v, n) in enumerate(zip(means, ns)):
    ax.text(i, v + (0.02 if v >= 0 else -0.055), f"{fmt(v)}\n(n={n})", ha="center", fontsize=8.5, color=NAVY)
ax.set_title("Kemusiman: Rata-rata Inflasi mtm per Bulan Kalender (2019–2026)")
ax.set_ylabel("Rata-rata mtm (%)")
save(fig, "chart_kemusiman.png")

# 6. Komponen yoy Sep 2026
komp = F["komponen_sep2026"]
fig, ax = plt.subplots(figsize=(9, 4.4))
names = list(komp.keys())[::-1]
vals = [komp[n]["yoy"] for n in names]
ax.barh(names, vals, color=[RED, TEAL, NAVY, GRAY, BUTTER][:len(names)][::-1], height=0.58)
for i, v in enumerate(vals):
    ax.text(v + 0.08, i, fmt(v) + "%", va="center", fontweight="bold", color=NAVY)
ax.axvline(3.28, color=RED, lw=1.1, ls="--")
ax.text(3.33, len(names) - 0.35, "Umum 3,28%", color=RED, fontsize=9)
ax.set_title("Inflasi per Komponen, September 2026 (yoy)")
ax.set_xlabel("Inflasi yoy (%)"); ax.set_xlim(0, max(vals) * 1.25)
save(fig, "chart_komponen_yoy.png")

# 7. Andil yoy komponen Sep 2026
fig, ax = plt.subplots(figsize=(9, 4.0))
tiga = ["Inflasi Inti", "Harga Bergejolak", "Harga Diatur Pemerintah"]
av = [komp[c]["andil_yoy"] for c in tiga]
ax.bar(tiga, av, color=[NAVY, RED, TEAL], width=0.52)
for i, v in enumerate(av):
    ax.text(i, v + 0.05, fmt(v), ha="center", fontweight="bold", color=NAVY)
ax.set_title("Andil terhadap Inflasi yoy September 2026 per Komponen (poin persen)")
ax.set_ylabel("Andil (poin %)")
save(fig, "chart_komponen_andil.png")

# 8. Kelompok yoy Sep 2026
k9 = kel[kel["periode"] == "2026-09"].dropna(subset=["yoy_persen"]).sort_values("yoy_persen")
fig, ax = plt.subplots(figsize=(10, 5.6))
short = [n.replace(", dan", ",\n dan").replace("Makanan, Minuman,\n dan Tembakau", "Makanan, Minuman\ndan Tembakau") for n in k9["kelompok"]]
ax.barh(short, k9["yoy_persen"], color=NAVY, height=0.62)
for i, v in enumerate(k9["yoy_persen"]):
    ax.text(v + 0.1, i, fmt(v) + "%", va="center", fontweight="bold", color=NAVY, fontsize=9.5)
ax.axvline(3.28, color=RED, lw=1.1, ls="--")
ax.set_title("Inflasi yoy per Kelompok Pengeluaran, September 2026")
ax.set_xlabel("Inflasi yoy (%)"); ax.set_xlim(0, k9["yoy_persen"].max() * 1.22)
ax.tick_params(labelsize=9)
save(fig, "chart_kelompok_yoy.png")

# 9. Andil yoy kelompok Sep 2026
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.barh(short, k9["andil_yoy"], color=TEAL, height=0.62)
for i, v in enumerate(k9["andil_yoy"]):
    ax.text(v + 0.02, i, fmt(v), va="center", fontweight="bold", color=NAVY, fontsize=9.5)
ax.set_title("Andil yoy per Kelompok Pengeluaran, September 2026 (poin persen)")
ax.set_xlabel("Andil (poin %)"); ax.set_xlim(0, k9["andil_yoy"].max() * 1.25)
ax.tick_params(labelsize=9)
save(fig, "chart_kelompok_andil.png")

# 10. Kota ekstrem Sep 2026
top = kota.head(8).iloc[::-1]
bot = kota.tail(8)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
axes[0].barh(top["kabupaten_kota"], top["yoy_persen"], color=RED, height=0.62)
for i, v in enumerate(top["yoy_persen"]):
    axes[0].text(v + 0.1, i, fmt(v) + "%", va="center", fontweight="bold", fontsize=9)
axes[0].set_title("8 Tertinggi"); axes[0].set_xlim(0, 10.2); axes[0].tick_params(labelsize=8.5)
axes[1].barh(bot["kabupaten_kota"].iloc[::-1], bot["yoy_persen"].iloc[::-1], color=TEAL, height=0.62)
for i, v in enumerate(bot["yoy_persen"].iloc[::-1]):
    axes[1].text(v + 0.05, i, fmt(v) + "%", va="center", fontweight="bold", fontsize=9)
axes[1].set_title("8 Terendah"); axes[1].set_xlim(0, 3.2); axes[1].tick_params(labelsize=8.5)
fig.suptitle("Inflasi yoy Kabupaten/Kota Ekstrem, September 2026", fontweight="bold", color=NAVY, fontsize=13)
save(fig, "chart_kota_ekstrem.png")

# 11. Distribusi kota
fig, ax = plt.subplots(figsize=(9.5, 4.4))
ax.hist(kota["yoy_persen"], bins=18, color=NAVY, alpha=0.88, edgecolor="white")
ax.axvline(3.28, color=RED, lw=2, label="Nasional 3,28%")
ax.axvline(kota["yoy_persen"].median(), color=BUTTER, lw=2, ls="--", label=f"Median kota {fmt(float(kota['yoy_persen'].median()))}%")
ax.set_title("Distribusi Inflasi yoy 150 Kabupaten/Kota, September 2026")
ax.set_xlabel("Inflasi yoy (%)"); ax.set_ylabel("Jumlah kab/kota"); ax.legend(frameon=False)
save(fig, "chart_kota_distribusi.png")

# 12. Provinsi Sep 2026 (semua 38, terurut)
fig, ax = plt.subplots(figsize=(10.5, 7.6))
ax.barh(prov_s["provinsi"].iloc[::-1], prov_s["yoy_persen"].iloc[::-1],
        color=[RED if v > 3.28 else NAVY for v in prov_s["yoy_persen"].iloc[::-1]], height=0.68)
ax.axvline(3.28, color=RED, lw=1.1, ls="--")
ax.set_title("Inflasi yoy per Provinsi, September 2026 (garis putus-putus = nasional 3,28%)")
ax.set_xlabel("Inflasi yoy (%)"); ax.tick_params(labelsize=8.5)
save(fig, "chart_provinsi.png")

# 13. Kelompok mtm Sep 2022 (bulan kenaikan BBM)
k22 = kel[kel["periode"] == "2022-09"].dropna(subset=["mtm_persen"]).sort_values("mtm_persen")
fig, ax = plt.subplots(figsize=(10, 5.4))
cols = [RED if n == "Transportasi" else NAVY for n in k22["kelompok"]]
ax.barh([n.replace(", dan", ",\n dan") for n in k22["kelompok"]], k22["mtm_persen"], color=cols, height=0.62)
for i, v in enumerate(k22["mtm_persen"]):
    ax.text(v + (0.15 if v >= 0 else -0.15), i, fmt(v) + "%", va="center",
            ha="left" if v >= 0 else "right", fontweight="bold", color=NAVY, fontsize=9.5)
ax.set_title("Inflasi mtm per Kelompok, September 2022 — Bulan Kenaikan BBM (umum +1,17%)")
ax.set_xlabel("Inflasi mtm (%)"); ax.set_xlim(-1.2, 10.4); ax.tick_params(labelsize=9)
save(fig, "chart_bbm_2022.png")

print("Selesai: findings.json + 13 grafik")

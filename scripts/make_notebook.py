#!/usr/bin/env python3
"""Menghasilkan analysis.ipynb: notebook pendamping proyek Inflasi."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": src.splitlines(keepends=True)}


cells = [
    md("# Analisis Inflasi Indonesia 2026\n"
       "Notebook pendamping `scripts/analysis.py`: memuat data terkompilasi dari BRS BPS, "
       "memverifikasi jangkar inflasi tahunan, dan menghitung ulang temuan utama. "
       "Keterangan lengkap sumber ada di `data/SOURCES.md`."),
    code("import pandas as pd\n"
         "import matplotlib.pyplot as plt\n\n"
         "nas = pd.read_csv('data/inflasi_nasional_bulanan.csv')\n"
         "kom = pd.read_csv('data/inflasi_komponen.csv')\n"
         "kel = pd.read_csv('data/inflasi_kelompok.csv')\n"
         "kota = pd.read_csv('data/inflasi_kota_2026_09.csv')\n"
         "nas.head(3)"),
    md("## Verifikasi jangkar: inflasi tahunan Desember\n"
       "Angka Desember (yoy) harus cocok dengan angka resmi BPS untuk setiap tahun."),
    code("jangkar = {2019: 2.72, 2020: 1.68, 2021: 1.87, 2022: 5.51, 2023: 2.61, 2024: 1.57, 2025: 2.92}\n"
         "des = nas[nas.bulan == 12].set_index('tahun')['yoy_persen']\n"
         "for th, target in jangkar.items():\n"
         "    print(th, des[th], 'OK' if des[th] == target else 'SELISIH')"),
    md("## Posisi terbaru dan puncak seri"),
    code("terbaru = nas[nas.periode == '2026-09'].iloc[0]\n"
         "print('Sep 2026: yoy', terbaru.yoy_persen, '| mtm', terbaru.mtm_persen, '| IHK', terbaru.ihk)\n"
         "puncak = nas.loc[nas.yoy_persen.idxmax()]\n"
         "print('Puncak yoy:', puncak.periode, puncak.yoy_persen, '(bulan kenaikan BBM, bukan Oktober)')"),
    md("## Bulan deflasi\n"
       "Bulan dengan mtm negatif. Terdalam adalah Februari 2025 (diskon tarif listrik), "
       "dan era COVID menyumbang tiga bulan berurutan pada 2020."),
    code("deflasi = nas[nas.mtm_persen < 0].sort_values('mtm_persen')\n"
         "print('Jumlah bulan deflasi teramati:', len(deflasi))\n"
         "deflasi[['periode', 'mtm_persen']]"),
    md("## Sasaran Bank Indonesia 2,5% +/- 1%\n"
       "Berapa bulan dari 24 bulan terakhir yang berada di dalam rentang 1,5% sampai 3,5%?"),
    code("jendela = nas[nas.periode >= '2024-10'].dropna(subset=['yoy_persen'])\n"
         "dalam = jendela[jendela.yoy_persen.between(1.5, 3.5)]\n"
         "print(f'{len(dalam)} dari {len(jendela)} bulan di dalam sasaran')\n"
         "print('Di bawah:', jendela[jendela.yoy_persen < 1.5].periode.tolist())\n"
         "print('Di atas :', jendela[jendela.yoy_persen > 3.5].periode.tolist())"),
    md("## Tren yoy 2023 sampai 2026"),
    code("d = nas[nas.periode >= '2023-01'].dropna(subset=['yoy_persen']).copy()\n"
         "d['tanggal'] = pd.to_datetime(d.periode)\n"
         "fig, ax = plt.subplots(figsize=(11, 4.6))\n"
         "ax.axhspan(1.5, 3.5, color='#F2C14E', alpha=0.35, label='Sasaran BI 1,5% - 3,5%')\n"
         "ax.plot(d.tanggal, d.yoy_persen, color='#14406B', lw=2, marker='o', ms=3)\n"
         "ax.set_title('Inflasi yoy Indonesia, Jan 2023 - Sep 2026'); ax.legend(); plt.show()"),
    md("## Komponen September 2026\n"
       "Harga bergejolak tertinggi lajunya, tetapi andil terbesar datang dari inti."),
    code("k9 = kom[kom.periode == '2026-09'].set_index('komponen')\n"
         "k9[['yoy_persen', 'mtm_persen', 'andil_yoy']]"),
    md("## Kelompok pengeluaran September 2026"),
    code("kel[kel.periode == '2026-09'].sort_values('andil_yoy', ascending=False)[['kelompok', 'yoy_persen', 'andil_yoy']]"),
    md("## Disparitas kabupaten/kota September 2026"),
    code("print('Tertinggi:', kota.iloc[0].kabupaten_kota, kota.iloc[0].yoy_persen)\n"
         "print('Terendah :', kota.iloc[-1].kabupaten_kota, kota.iloc[-1].yoy_persen)\n"
         "print('Rentang  :', round(kota.yoy_persen.max() - kota.yoy_persen.min(), 2), 'poin')\n"
         "print('Di atas nasional (3,28):', int((kota.yoy_persen > 3.28).sum()), 'dari', len(kota), 'kota')"),
    md("## Kemusiman mtm\n"
       "Rata-rata mtm per bulan kalender dari seluruh bulan yang terkompilasi."),
    code("nas.dropna(subset=['mtm_persen']).groupby('bulan')['mtm_persen'].agg(['mean', 'count']).round(2)"),
]

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3",
        "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"}},
      "nbformat": 4, "nbformat_minor": 5}
out = BASE / "analysis.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("Notebook:", out, "| sel:", len(cells))

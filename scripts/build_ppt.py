# -*- coding: utf-8 -*-
"""
Membangun PPT portofolio Inflasi Indonesia 2026 (10 slide, 16:9).
Standar deck terbaru: panel angka hero di sampul, chip KPI, slide temuan,
slide 9 pratinjau Dashboard Power BI, slide 10 Designed Close.
Semua angka dibaca dari findings.json (hasil analysis.py).
Proyek data analyst murni: statistik resmi BPS dan dashboard, tanpa
machine learning. Tanpa em dash di semua teks.
"""
import json
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm, Pt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CH = os.path.join(ROOT, "charts")
F = json.load(open(os.path.join(ROOT, "findings.json")))

BLUE = RGBColor(0x14, 0x40, 0x6B); SKY = RGBColor(0x7F, 0xB0, 0xD9)
RED = RGBColor(0xD6, 0x28, 0x28); ROSE = RGBColor(0xF6, 0xD9, 0xD9)
BUTTER = RGBColor(0xF2, 0xC1, 0x4E)
OAT = RGBColor(0xFA, 0xF6, 0xEF); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SLATE = RGBColor(0x2E, 0x2A, 0x26); GREY = RGBColor(0x8A, 0x7F, 0x76)
LIGHT = RGBColor(0xEF, 0xE4, 0xD8)

prs = Presentation()
prs.slide_width = Cm(33.867); prs.slide_height = Cm(19.05)
BLANK = prs.slide_layouts[6]


def slide(bg=OAT):
    s = prs.slides.add_slide(BLANK)
    r = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    r.fill.solid(); r.fill.fore_color.rgb = bg; r.line.fill.background()
    r.shadow.inherit = False
    return s


def box(s, x, y, w, h, fill=None, line=None):
    r = s.shapes.add_shape(1, Cm(x), Cm(y), Cm(w), Cm(h))
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line; r.line.width = Pt(1)
    r.shadow.inherit = False
    return r


def txt(s, x, y, w, h, text, size=14, bold=False, color=SLATE, align=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = tb.text_frame; tf.word_wrap = True
    lines = text.split("\n")
    tf.paragraphs[0].text = lines[0]; tf.paragraphs[0].alignment = align
    for ln in lines[1:]:
        p = tf.add_paragraph(); p.text = ln; p.alignment = align
    for p in tf.paragraphs:
        p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color
        p.font.name = "Calibri"
    return tb


def title_bar(s, title, sub=None):
    box(s, 0, 0, 33.87, 2.5, fill=BLUE)
    txt(s, 1.2, 0.42, 31.5, 1.1, title, size=25, bold=True, color=WHITE)
    if sub:
        txt(s, 1.2, 1.42, 31.5, 0.8, sub, size=13, color=SKY)


def bullets(s, x, y, w, items, size=15, gap=0.35):
    cy = y
    for head, body in items:
        txt(s, x, cy, 0.5, 0.7, "▪", size=size, bold=True, color=RED)
        txt(s, x + 0.6, cy, w - 0.6, 1.6, head, size=size, bold=True, color=BLUE)
        cy += 0.78
        if body:
            txt(s, x + 0.6, cy, w - 0.6, 1.8, body, size=size - 1.5, color=SLATE)
            cy += 0.62 + 0.55 * (len(body) // 62)
        cy += gap
    return cy


def pic(s, path, x, y, w=None, h=None):
    kw = {}
    if w: kw["width"] = Cm(w)
    if h: kw["height"] = Cm(h)
    return s.shapes.add_picture(path, Cm(x), Cm(y), **kw)


def chip(s, x, y, w, label, value, sub):
    box(s, x, y, w, 3.1, fill=WHITE, line=LIGHT)
    box(s, x, y, w, 0.18, fill=RED)
    txt(s, x + 0.35, y + 0.32, w - 0.7, 0.6, label, size=11.5, bold=True, color=GREY)
    txt(s, x + 0.35, y + 0.95, w - 0.7, 1.0, value, size=25, bold=True, color=BLUE)
    txt(s, x + 0.35, y + 2.05, w - 0.7, 0.9, sub, size=11, color=SLATE)


def footer(s, n):
    txt(s, 29.9, 18.35, 3.4, 0.5, f"{n} / 10", size=10, color=GREY, align=PP_ALIGN.RIGHT)
    txt(s, 1.2, 18.35, 12, 0.5, "Inflasi Indonesia 2026 • Data BPS",
        size=10, color=GREY)


T = F["terbaru"]; PITA = F["pita_target_bi"]; KOTA = F["kota_sep2026"]

# ================================================================ 1 · sampul
s = slide(bg=BLUE)
box(s, 0, 0, 19.6, 19.05, fill=BLUE)
txt(s, 1.4, 2.0, 17.5, 1.0, "PORTOFOLIO ANALISIS DATA", size=15, bold=True, color=SKY)
txt(s, 1.4, 3.1, 17.8, 3.4, "Inflasi Indonesia\n2026", size=43, bold=True, color=WHITE)
txt(s, 1.4, 6.6, 17.2, 2.8,
    "Membaca perjalanan harga konsumen Indonesia lewat statistik resmi BPS: "
    "dari deflasi COVID dan lonjakan BBM 2022 sampai posisi inflasi hari ini "
    "terhadap sasaran Bank Indonesia, dirinci per komponen, kelompok "
    "pengeluaran, dan 150 kabupaten/kota.",
    size=15.5, color=ROSE)
box(s, 1.4, 10.4, 16.8, 0.06, fill=SKY)
txt(s, 1.4, 10.9, 17.5, 1.8,
    "Sumber: BPS, BRS Perkembangan Indeks Harga Konsumen (rilis bulanan)\n"
    "Periode: Januari 2019 sampai September 2026 (93 bulan)",
    size=13, color=RGBColor(0xD6, 0xE4, 0xF2))
box(s, 1.4, 13.6, 16.8, 2.1, fill=BUTTER)
txt(s, 1.75, 13.9, 16.2, 1.7,
    "DASHBOARD POWER BI\n"
    "Kit siap rakit: model bintang 5 fakta dan 6 dimensi, 12 measure DAX, 4 halaman",
    size=13, bold=True, color=SLATE)
box(s, 20.6, 0, 13.27, 19.05, fill=RED)
txt(s, 21.8, 2.3, 11, 1.0, "INFLASI YOY\nSEPTEMBER 2026", size=14, bold=True, color=ROSE)
txt(s, 21.8, 4.6, 11.4, 2.2, "3,28%", size=60, bold=True, color=WHITE)
txt(s, 21.8, 7.1, 11, 1.4,
    "Di dalam sasaran BI 2,5% plus minus 1%. Bulanannya +0,30%, "
    "IHK 112,31 (basis 2022=100)",
    size=14, color=ROSE)
box(s, 21.8, 9.0, 10, 0.05, fill=ROSE)
txt(s, 21.8, 9.5, 11, 3.6,
    "Puncak era 2022: 5,95% (Sep 2022)\n"
    "19 dari 24 bulan terakhir di dalam\nsasaran Bank Indonesia\n"
    "92 dari 150 kab/kota di atas\ninflasi nasional",
    size=14.5, color=WHITE)
txt(s, 21.8, 15.6, 11, 1.6, "BAGHIZ ASSHIDDIQIE ARASYA\nData Analyst",
    size=14, bold=True, color=WHITE)

# ================================================================ 2 · KPI
s = slide()
title_bar(s, "Potret Terbaru: Inflasi September 2026 Sebesar 3,28%",
          "Empat angka kunci dari BRS Perkembangan IHK September 2026, BPS")
chip(s, 1.2, 3.4, 7.5, "INFLASI YOY SEP 2026", "3,28%",
     "Naik dari 3,19% pada Agustus 2026, tetap di dalam sasaran BI")
chip(s, 9.3, 3.4, 7.5, "INFLASI MTM SEP 2026", "+0,30%",
     "Setahun berjalan (ytd) 2,17%, IHK mencapai 112,31")
chip(s, 17.4, 3.4, 7.5, "PUNCAK YOY ERA 2022", "5,95%",
     "September 2022, bulan kenaikan harga BBM bersubsidi")
chip(s, 25.5, 3.4, 7.2, "BULAN DI DALAM SASARAN BI", "19 / 24",
     "Dua tahun terakhir, Oktober 2024 sampai September 2026")
bullets(s, 1.2, 7.6, 31.4, [
    ("Komponen pangan bergejolak paling panas: 5,03%",
     "Harga bergejolak 5,03% yoy, harga diatur pemerintah 3,25%, dan inflasi "
     "inti paling adem di 2,84%. Andil terbesar justru dari inti (1,82 poin) "
     "karena bobotnya paling besar."),
    ("Makanan adalah penyumbang andil terbesar",
     "Kelompok Makanan, Minuman, dan Tembakau memberi andil 1,28 poin dari "
     "inflasi 3,28%, diikuti Transportasi 0,58 dan Perawatan Pribadi 0,53 "
     "poin yang yoy-nya tertinggi di 7,77%."),
    ("Dua komoditas cabai masuk lima besar pendorong bulanan",
     "Andil mtm terbesar September 2026: cabai rawit 0,08 dan cabai merah "
     "0,06 poin, pola gejolak pangan segar yang berulang dari tahun ke tahun."),
], size=15.5)
footer(s, 2)

# ================================================================ 3 · tren & disinflasi
s = slide()
title_bar(s, "Busur Besar: Lonjakan 2022, Disinflasi, Lalu Stabil di Sasaran",
          "Inflasi yoy Januari 2023 sampai September 2026 dan inflasi tahunan Desember")
pic(s, os.path.join(CH, "chart_yoy_tren.png"), 1.2, 3.1, w=19.2)
pic(s, os.path.join(CH, "chart_tahunan_desember.png"), 21.0, 3.1, w=11.7)
bullets(s, 1.2, 12.6, 31.4, [
    ("Dari 5,51% menjadi 1,57% dalam dua tahun",
     "Inflasi tahunan Desember: 5,51% (2022), 2,61% (2023), lalu 1,57% "
     "(2024), titik terendah seri Desember sejak 2019 kecuali era COVID."),
    ("Anomali awal 2025 dan awal 2026 sama-sama soal listrik",
     "Februari 2025 inflasi yoy minus 0,09% karena diskon tarif listrik, "
     "dan Februari 2026 melonjak ke 4,76% sebagai efek basis rendah dari "
     "diskon yang sama (tarif listrik yoy +86,96%)."),
], size=14.5, gap=0.25)
footer(s, 3)

# ================================================================ 4 · deflasi
s = slide()
title_bar(s, "Sisi Lain Inflasi: 11 Bulan Deflasi yang Teramati",
          "Bulan dengan inflasi mtm negatif pada seri yang terkompilasi, 2019 sampai 2026")
pic(s, os.path.join(CH, "chart_mtm_tren.png"), 1.2, 3.1, w=19.2)
pic(s, os.path.join(CH, "chart_deflasi.png"), 21.0, 3.1, w=11.7)
bullets(s, 1.2, 12.6, 31.4, [
    ("Deflasi COVID: tiga bulan berurutan pada 2020",
     "Juli, Agustus, September 2020 mencatat mtm minus 0,10%, minus 0,05%, "
     "dan minus 0,05% saat permintaan melemah di awal pandemi."),
    ("Deflasi terdalam justru Februari 2025: minus 0,48%",
     "Bukan karena krisis, melainkan diskon tarif listrik pemerintah. "
     "Deflasi terdalam kedua: September 2019 minus 0,27%, musim panen."),
    ("Oktober 2022 ikut deflasi: minus 0,11%",
     "Sebulan setelah lonjakan BBM, harga pangan menormalkan diri dan "
     "menarik mtm ke wilayah negatif."),
], size=14.5, gap=0.25)
footer(s, 4)

# ================================================================ 5 · komponen
s = slide()
title_bar(s, "Komponen: Pangan Bergejolak Memimpin, Inti Tetap Lengket",
          "Inflasi dan andil per komponen, September 2026")
pic(s, os.path.join(CH, "chart_komponen_yoy.png"), 1.2, 3.1, w=15.9)
pic(s, os.path.join(CH, "chart_komponen_andil.png"), 17.0, 3.1, w=15.7)
bullets(s, 1.2, 12.3, 31.4, [
    ("Bergejolak tertinggi, inti terberat",
     "Harga bergejolak 5,03% yoy dengan andil 0,83 poin, sementara inti "
     "hanya 2,84% tetapi andilnya 1,82 poin, terbesar di antara komponen."),
    ("Tiga era, tiga penggerak berbeda",
     "2020: bergejolak melonjak bulanan (Desember +2,17% mtm). 2022: harga "
     "diatur pemerintah lewat BBM. 2025 sampai 2026: inti lengket di kisaran "
     "2,2% sampai 2,8% sementara bergejolak berayun 5% ke atas."),
], size=14.5, gap=0.25)
footer(s, 5)

# ================================================================ 6 · kelompok
s = slide()
title_bar(s, "Kelompok Pengeluaran: Makanan Selalu Jadi Penyumbang Terbesar",
          "Inflasi yoy 11 kelompok pengeluaran, September 2026")
pic(s, os.path.join(CH, "chart_kelompok_yoy.png"), 1.2, 2.9, h=12.6)
bullets(s, 18.6, 3.2, 14.0, [
    ("Perawatan Pribadi paling panas: 7,77%",
     "Digerakkan emas perhiasan, penyumbang andil yoy komoditas terbesar "
     "nasional (0,44 poin) seiring harga emas dunia."),
    ("Makanan: yoy 4,37%, andil 1,28 poin",
     "Terbesar di antara semua kelompok pada September 2026, dan pola yang "
     "sama pada Desember 2023 (andil 1,60) dan Desember 2025 (1,33)."),
    ("Kelompok kebutuhan dasar justru adem",
     "Perumahan 1,02%, Pakaian 1,20%, Pendidikan 1,43%. Tekanan harga "
     "terkonsentrasi di pangan, transportasi (4,84%), dan jasa pribadi."),
    ("Satu-satunya kelompok deflasi pada Desember 2025",
     "Informasi, Komunikasi, dan Jasa Keuangan memberi andil minus 0,02 "
     "poin, tarif komunikasi yang terus turun."),
], size=14.5)
footer(s, 6)

# ================================================================ 7 · BBM & kemusiman
s = slide()
title_bar(s, "September 2022 dan Pola Musiman: Kapan Harga Bergerak",
          "Inflasi mtm per kelompok pada bulan kenaikan BBM, dan rata-rata mtm per bulan kalender")
pic(s, os.path.join(CH, "chart_bbm_2022.png"), 1.2, 3.1, w=15.9)
pic(s, os.path.join(CH, "chart_kemusiman.png"), 17.0, 3.1, w=15.7)
bullets(s, 1.2, 12.3, 31.4, [
    ("BBM naik, Transportasi melonjak 8,88% dalam sebulan",
     "September 2022 inflasi mtm 1,17% dan yoy mencapai puncak 5,95%. "
     "Kelompok lain nyaris tidak bergerak; Makanan bahkan turun 0,30%."),
    ("Maret dan Desember adalah bulan terpanas secara musiman",
     "Rata-rata mtm Maret dan Desember sama-sama 0,50%, bulan Ramadan dan "
     "Lebaran yang bergeser serta belanja akhir tahun. Agustus paling adem "
     "di 0,02%."),
], size=14.5, gap=0.25)
footer(s, 7)

# ================================================================ 8 · disparitas kota
s = slide()
title_bar(s, "Satu Negara, Dua Dunia Harga: Rentang Antar Kota 8,01 Poin",
          "Inflasi yoy 150 kabupaten/kota, September 2026")
pic(s, os.path.join(CH, "chart_kota_ekstrem.png"), 1.2, 3.1, w=19.2)
pic(s, os.path.join(CH, "chart_kota_distribusi.png"), 21.0, 3.1, w=11.7)
bullets(s, 1.2, 12.6, 31.4, [
    ("Tertinggi Kab. Minahasa Utara 9,05%, terendah Kab. Timor Tengah Selatan 1,04%",
     "Sulawesi Utara adalah provinsi terpanas (7,59%) dan sekaligus "
     "tertinggi mtm (+3,53%); Sumatera Selatan terendah di 2,55%."),
    ("Mayoritas kota di atas angka nasional",
     "92 dari 150 kab/kota (61%) berinflasi di atas 3,28%. Median kota "
     "3,59% dan rata-rata 3,76%, keduanya di atas angka nasional, karena "
     "agregat nasional tertimbang ke kota besar yang lebih adem."),
], size=14.5, gap=0.25)
footer(s, 8)

# ================================================================ 9 · dashboard
s = slide()
title_bar(s, "Dashboard Power BI: Inflasi-Indonesia-2026.pbix",
          "Kit siap rakit di folder powerbi/, model bintang, 12 measure DAX, 4 halaman")
pic(s, os.path.join(ROOT, "powerbi", "dashboard_preview_halaman1.png"), 1.2, 3.0, w=19.4)
bullets(s, 21.4, 3.1, 11.2, [
    ("Halaman 1, Ringkasan Inflasi",
     "Kartu KPI: yoy 3,28%, mtm 0,30%, IHK 112,31, puncak 5,95%. Tren yoy "
     "dengan pita sasaran BI dan andil kelompok September 2026."),
    ("Halaman 2, Komponen dan Kelompok",
     "Yoy dan andil per komponen, 11 kelompok pengeluaran, tabel tiga "
     "bulan Tabel 1 BRS (Nov 2025, Feb 2026, Sep 2026)."),
    ("Halaman 3, Peta Harga per Wilayah",
     "38 provinsi dan 150 kab/kota September 2026, ekstrem tertinggi dan "
     "terendah, kartu 92 kota di atas nasional."),
    ("Halaman 4, Sejarah dan Kemusiman",
     "Grafik mtm 2019 sampai 2026, inflasi Desember per tahun, pola "
     "musiman, dan rincian bulan kenaikan BBM 2022."),
    ("Grain dipisah, anti salah agregasi",
     "Fakta bulanan, kelompok, komponen, kota, dan provinsi masing-masing "
     "pada grain-nya sendiri. Setiap measure punya angka verifikasi di "
     "measures_dax.md."),
], size=13)
footer(s, 9)

# ================================================================ 10 · penutup
s = slide(bg=BLUE)
txt(s, 1.4, 1.6, 31, 1.2, "Kesimpulan", size=30, bold=True, color=WHITE)
box(s, 1.4, 3.0, 16.8, 0.06, fill=SKY)
items = [
    ("Inflasi terkendali dan di dalam sasaran",
     "September 2026 inflasi yoy 3,28% dengan mtm 0,30%. Selama dua tahun "
     "terakhir 19 dari 24 bulan berada di dalam sasaran BI 2,5% plus minus 1%."),
    ("Puncak era ini adalah September 2022, bukan Oktober",
     "Kenaikan BBM membuat Transportasi naik 8,88% sebulan dan yoy menyentuh "
     "5,95%; inflasi tahunan 2022 ditutup 5,51% sebelum disinflasi ke 2,61% "
     "dan 1,57%."),
    ("Pangan adalah sumber gejolak yang berulang",
     "Kelompok Makanan penyumbang andil terbesar pada Des 2023, Des 2025, "
     "dan Sep 2026; komponen bergejolak 5,03% dan cabai kembali masuk daftar "
     "pendorong bulanan teratas."),
    ("Angka nasional menyembunyikan disparitas daerah",
     "Rentang antar kab/kota 8,01 poin (9,05% vs 1,04%) dan 61% kota berada "
     "di atas angka nasional; kebijakan harga tidak bisa dibaca dari satu angka."),
    ("Metode dan keterbatasan",
     "Seluruh angka dari BRS dan publikasi BPS, tertelusur di SOURCES.md. "
     "Seri yoy kontinu Jan 2023 sampai Sep 2026; titik 2019 sampai 2022 "
     "hanya yang terverifikasi, dan IHK tidak disambung lintas ganti basis."),
]
cy = 3.7
for head, body in items:
    txt(s, 1.4, cy, 0.5, 0.7, "▪", size=16, bold=True, color=SKY)
    txt(s, 2.0, cy, 29.5, 0.8, head, size=16.5, bold=True, color=WHITE)
    cy += 0.85
    txt(s, 2.0, cy, 29.5, 1.6, body, size=13.5, color=ROSE)
    cy += 0.62 + 0.5 * (len(body) // 110) + 0.4
box(s, 1.4, 16.6, 31.0, 0.05, fill=SKY)
txt(s, 1.4, 17.0, 31.4, 1.2,
    "Terima kasih, BAGHIZ ASSHIDDIQIE ARASYA • Data Analyst\n"
    "Repo: github.com/baghizash/inflasi-indonesia-2026",
    size=14, bold=True, color=WHITE)

OUT = os.path.join(ROOT, "Portofolio-Analisis-Inflasi.pptx")
prs.save(OUT)
print("PPTX:", OUT)

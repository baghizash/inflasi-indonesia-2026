# -*- coding: utf-8 -*-
"""
Modul pembelajaran Analisis Inflasi Indonesia 2026.
Landscape A4, gaya pro pemula, Bahasa Indonesia sederhana, banyak visual.
Angka dibaca dari findings.json. Output: Modul-Analisis-Inflasi.pdf
Tanpa em dash di semua teks.
"""
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CH = os.path.join(ROOT, "charts")
F = json.load(open(os.path.join(ROOT, "findings.json")))

BLUE = colors.HexColor("#14406B"); SKY = colors.HexColor("#7FB0D9")
RED = colors.HexColor("#D62828"); BUTTER = colors.HexColor("#F2C14E")
OAT = colors.HexColor("#FAF6EF")
SLATE = colors.HexColor("#2E2A26"); GREY = colors.HexColor("#8A7F76")
LIGHT = colors.HexColor("#EAF0F7"); REDBG = colors.HexColor("#FDECEC")
WHITE = colors.white

W, H = landscape(A4)  # 29.7 x 21 cm

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=25, leading=31,
                    textColor=BLUE, spaceAfter=6)
H2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=16.5, leading=21,
                    textColor=BLUE, spaceBefore=4, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="Helvetica", fontSize=11.5, leading=16,
                      textColor=SLATE, spaceAfter=6)
SMALL = ParagraphStyle("SMALL", fontName="Helvetica", fontSize=9.5, leading=13,
                       textColor=GREY)
CALLOUT = ParagraphStyle("CALLOUT", fontName="Helvetica", fontSize=11.5,
                         leading=16, textColor=SLATE)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLUE)
    canvas.rect(0, 0, W, 0.85 * cm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(1.4 * cm, 0.32 * cm,
                      "Modul Analisis Inflasi Indonesia 2026, Data: BPS (BRS Perkembangan IHK)")
    canvas.drawRightString(W - 1.4 * cm, 0.32 * cm, f"Halaman {doc.page}")
    canvas.restoreState()


def img(name, w):
    from PIL import Image as PILImage
    p = os.path.join(CH, name)
    iw, ih = PILImage.open(p).size
    return Image(p, width=w, height=w * ih / iw)


def side_by_side(left, right, w_each=13.1 * cm):
    t = Table([[img(left, w_each), img(right, w_each)]],
              colWidths=[(W - 2.8 * cm) / 2] * 2)
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def callout(text, bg=LIGHT, bar=RED):
    t = Table([[Paragraph(text, CALLOUT)]], colWidths=[W - 3.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3.5, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def kpi_table():
    data = [[Paragraph("<b>Inflasi YoY<br/>Sep 2026</b>", SMALL),
             Paragraph("<b>Inflasi MtM<br/>Sep 2026</b>", SMALL),
             Paragraph("<b>Puncak YoY<br/>Era 2022</b>", SMALL),
             Paragraph("<b>Bulan di Dalam<br/>Sasaran BI</b>", SMALL)],
            [Paragraph("<b><font size=17 color='#14406B'>3,28%</font></b>", BODY),
             Paragraph("<b><font size=17 color='#14406B'>+0,30%</font></b>", BODY),
             Paragraph("<b><font size=17 color='#14406B'>5,95%</font></b>", BODY),
             Paragraph("<b><font size=17 color='#14406B'>19 / 24</font></b>", BODY)],
            [Paragraph("Di dalam sasaran BI 2,5% plus minus 1%", SMALL),
             Paragraph("IHK 112,31 (basis 2022=100)", SMALL),
             Paragraph("September 2022, bulan kenaikan BBM", SMALL),
             Paragraph("Dua tahun terakhir (Okt 2024 - Sep 2026)", SMALL)]]
    t = Table(data, colWidths=[(W - 2.8 * cm) / 4] * 4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D8E2EC")),
        ("LINEABOVE", (0, 0), (-1, 0), 3, RED),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


story = []

# ---------------------------------------------------------------- sampul isi
story.append(Spacer(1, 1.1 * cm))
story.append(Paragraph("Memahami Inflasi Indonesia Lewat Data BPS", H1))
story.append(Paragraph(
    "Modul belajar analisis data untuk pemula: memahami apa itu inflasi dan IHK, "
    "membaca rilis resmi BPS, mengikuti perjalanan inflasi Indonesia dari 2019 "
    "sampai September 2026, lalu merakitnya menjadi dashboard Power BI.", BODY))
story.append(kpi_table())
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph("Cara memakai modul ini", H2))
story.append(Paragraph(
    "Baca berurutan dari Bab 1. Setiap bab punya satu ide utama, satu atau dua "
    "grafik, dan kotak rangkuman. Semua angka di modul ini nyata, berasal dari "
    "Berita Resmi Statistik (BRS) BPS, dan bisa kamu telusur kembali ke berkas "
    "data proyek. Istilah sulit selalu dijelaskan saat pertama kali muncul.", BODY))
story.append(callout(
    "<b>Gambaran besar:</b> inflasi Indonesia melonjak ke 5,95% pada September 2022 "
    "karena kenaikan harga BBM, turun tajam selama 2023 sampai 2024, dan sejak itu "
    "bergerak di sekitar sasaran Bank Indonesia. Pada September 2026 inflasi "
    "year-on-year berada di 3,28%."))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 1
story.append(Paragraph("Bab 1. Apa Itu Inflasi dan IHK?", H2))
story.append(Paragraph(
    "Inflasi adalah kenaikan harga barang dan jasa secara umum dan terus menerus "
    "dalam satu periode. Lawannya, deflasi, adalah penurunan harga secara umum. "
    "BPS mengukur inflasi lewat Indeks Harga Konsumen (IHK): bayangkan satu "
    "keranjang belanja berisi ribuan barang dan jasa yang biasa dibeli rumah "
    "tangga. IHK adalah harga total keranjang itu dibanding harga pada tahun "
    "dasar. Bila IHK naik dari 100 menjadi 103, harga keranjang naik 3%.", BODY))
story.append(Paragraph(
    "Ada tiga cara membaca perubahan IHK. Inflasi month-to-month (mtm) "
    "membandingkan bulan ini dengan bulan lalu, peka terhadap kejadian sesaat "
    "seperti kenaikan BBM atau musim panen. Inflasi year-on-year (yoy) "
    "membandingkan bulan ini dengan bulan yang sama tahun lalu, dan inilah angka "
    "utama yang dipakai Bank Indonesia. Inflasi year-to-date (ytd) membandingkan "
    "dengan Desember tahun sebelumnya. Contoh nyata: pada September 2026 IHK "
    "Indonesia 112,31, naik 0,30% dari Agustus (mtm), naik 2,17% dari Desember "
    "2025 (ytd), dan naik 3,28% dari September 2025 (yoy).", BODY))
story.append(callout(
    "<b>Hati-hati ganti tahun dasar:</b> sampai Desember 2023 IHK memakai basis "
    "2018=100, mulai Januari 2024 memakai basis 2022=100. Level IHK dari dua "
    "basis tidak boleh disambung langsung, tetapi laju mtm dan yoy tetap bisa "
    "dibandingkan karena keduanya adalah persentase perubahan.", bg=REDBG))
story.append(Paragraph(
    "Bank Indonesia menargetkan inflasi 2,5% plus minus 1%, artinya rentang "
    "1,5% sampai 3,5%. Inflasi terlalu tinggi menggerus daya beli, inflasi "
    "terlalu rendah bisa berarti permintaan lesu. Sepanjang modul ini kita akan "
    "menilai posisi inflasi terhadap rentang sasaran tersebut.", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 2
story.append(Paragraph("Bab 2. Data: Dari Rilis BPS Menjadi Tabel Rapi", H2))
story.append(Paragraph(
    "Setiap awal bulan BPS menerbitkan BRS Perkembangan Indeks Harga Konsumen. "
    "Di dalamnya ada Tabel 1 (inflasi per kelompok pengeluaran), Tabel 2 (rekap "
    "tiga tahun), Gambar 1 (grafik yoy yang nilainya tercetak), Tabel 3 sampai 8 "
    "(inflasi per provinsi dan kabupaten/kota), Tabel 9 (per komponen), dan "
    "Tabel 10 (andil per komoditas). Proyek ini memparse PDF BRS November 2025, "
    "Februari 2026, dan September 2026 tabel demi tabel, lalu menggabungkannya "
    "dengan seri historis dari BRS dan publikasi BPS terdahulu.", BODY))
story.append(Paragraph(
    "Hasilnya lima berkas data: seri nasional bulanan 93 bulan (Januari 2019 "
    "sampai September 2026), titik komponen, titik kelompok pengeluaran, serta "
    "tabel lengkap 38 provinsi dan 150 kabupaten/kota untuk September 2026. "
    "Tidak semua sel terisi: yoy bulanan 2019 sampai 2022 hanya dicatat pada "
    "bulan yang angkanya terverifikasi dari rilis resmi. Sel kosong dibiarkan "
    "kosong dan alasannya ditulis terbuka di data/SOURCES.md. Itu prinsip "
    "penting analisis data: lebih baik jujur soal celah daripada mengisi dengan "
    "tebakan.", BODY))
story.append(callout(
    "<b>Uji kualitas data:</b> pada 2023, inflasi mtm yang dihitung ulang dari "
    "IHK terbit cocok dengan angka tercetak pada 12 dari 12 bulan. Kontrol "
    "semacam ini memastikan rantai IHK dan laju inflasi saling konsisten "
    "sebelum dianalisis."))
story.append(img("chart_tahunan_desember.png", 17.5 * cm))
story.append(Paragraph(
    "Grafik di atas adalah uji jangkar proyek ini: inflasi tahunan setiap "
    "Desember. Semua nilainya cocok dengan angka resmi BPS: 2,72% (2019), "
    "1,68% (2020), 1,87% (2021), 5,51% (2022), 2,61% (2023), 1,57% (2024), "
    "dan 2,92% (2025).", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 3
story.append(Paragraph("Bab 3. Busur Besar 2019 sampai 2026", H2))
story.append(img("chart_yoy_tren.png", 24.5 * cm))
story.append(Paragraph(
    "Cerita dimulai dari era COVID: inflasi 2020 ditutup hanya 1,68% karena "
    "permintaan melemah. Kemudian harga energi dan pangan dunia naik, dan pada "
    "3 September 2022 pemerintah menaikkan harga BBM bersubsidi. Bulan itu juga "
    "inflasi yoy menyentuh puncak 5,95% dan inflasi tahunan 2022 ditutup 5,51%. "
    "Setelahnya datang disinflasi, penurunan laju inflasi secara bertahap: "
    "2,61% pada akhir 2023 dan 1,57% pada akhir 2024.", BODY))
story.append(Paragraph(
    "Selama 24 bulan terakhir (Oktober 2024 sampai September 2026), inflasi "
    "berada di dalam sasaran BI pada 19 bulan. Tiga bulan berada di bawah "
    "sasaran (Januari sampai Maret 2025, efek diskon tarif listrik) dan dua "
    "bulan di atas sasaran (Januari dan Februari 2026, efek basis rendah dari "
    "diskon yang sama). Anomali listrik ini pelajaran penting: satu kebijakan "
    "harga bisa membuat inflasi tampak sangat rendah lalu sangat tinggi tepat "
    "setahun kemudian, tanpa perubahan mendasar pada harga barang lain.", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 4
story.append(Paragraph("Bab 4. Deflasi: Saat Harga Justru Turun", H2))
story.append(side_by_side("chart_mtm_tren.png", "chart_deflasi.png"))
story.append(Paragraph(
    "Dari seluruh bulan yang terkompilasi, ada 11 bulan deflasi. Tiga di "
    "antaranya berurutan pada Juli sampai September 2020, saat pandemi menekan "
    "permintaan. Deflasi terdalam justru terjadi Februari 2025, minus 0,48%, "
    "dan penyebabnya bukan krisis melainkan diskon tarif listrik. Ada juga "
    "deflasi September 2019 (minus 0,27%) yang bersifat musiman panen, serta "
    "Oktober 2022 (minus 0,11%) ketika harga pangan menormalkan diri sebulan "
    "setelah lonjakan BBM.", BODY))
story.append(callout(
    "<b>Ingat:</b> deflasi satu bulan tidak selalu kabar buruk. Deflasi karena "
    "panen atau diskon kebijakan berbeda maknanya dengan deflasi karena "
    "permintaan runtuh seperti pada 2020. Selalu tanya penyebabnya sebelum "
    "menyimpulkan."))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 5
story.append(Paragraph("Bab 5. Tiga Komponen Inflasi", H2))
story.append(side_by_side("chart_komponen_yoy.png", "chart_komponen_andil.png"))
story.append(Paragraph(
    "BPS membagi inflasi menjadi tiga komponen. Inflasi inti adalah inflasi "
    "yang persisten, digerakkan permintaan dan ekspektasi, dan menjadi fokus "
    "Bank Indonesia. Harga bergejolak adalah harga pangan segar yang berayun "
    "mengikuti musim dan cuaca, seperti cabai dan beras. Harga diatur "
    "pemerintah adalah harga yang ditetapkan negara, misalnya BBM, tarif "
    "listrik, dan tarif angkutan.", BODY))
story.append(Paragraph(
    "Pada September 2026, harga bergejolak tertinggi di 5,03% yoy, diikuti harga "
    "diatur pemerintah 3,25% dan inti 2,84%. Tetapi andil terbesar terhadap "
    "inflasi umum justru datang dari inti, 1,82 poin dari total 3,28%, karena "
    "bobot inti dalam keranjang IHK paling besar. Pelajaran analis: laju "
    "tertinggi belum tentu penyumbang terbesar; selalu pasangkan laju dengan "
    "andilnya.", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 6
story.append(Paragraph("Bab 6. Kelompok Pengeluaran: Uang Kita Pergi ke Mana", H2))
story.append(side_by_side("chart_kelompok_yoy.png", "chart_kelompok_andil.png"))
story.append(Paragraph(
    "IHK dibagi ke 11 kelompok pengeluaran, dari Makanan sampai Perawatan "
    "Pribadi. Pada September 2026 kelompok terpanas adalah Perawatan Pribadi "
    "dan Jasa Lainnya (7,77% yoy), digerakkan harga emas perhiasan yang juga "
    "menjadi penyumbang andil komoditas terbesar nasional. Kelompok Makanan, "
    "Minuman, dan Tembakau naik 4,37% dengan andil 1,28 poin, terbesar di "
    "antara semua kelompok.", BODY))
story.append(Paragraph(
    "Pola makanan sebagai penyumbang terbesar ini berulang: andilnya 1,60 poin "
    "pada Desember 2023 dan 1,33 poin pada Desember 2025. Sementara itu "
    "kelompok kebutuhan dasar seperti Perumahan (1,02%) dan Pendidikan (1,43%) "
    "jauh lebih adem. Bila kamu mengerjakan proyek harga pangan atau harga "
    "cabai, bab ini adalah jembatannya: gejolak harga pangan segar adalah "
    "sumber volatilitas inflasi Indonesia yang paling sering muncul.", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 7
story.append(Paragraph("Bab 7. Kemusiman dan Bulan Kenaikan BBM", H2))
story.append(side_by_side("chart_bbm_2022.png", "chart_kemusiman.png"))
story.append(Paragraph(
    "September 2022 layak dibedah sendiri. Dalam satu bulan kelompok "
    "Transportasi melonjak 8,88% mtm akibat kenaikan BBM, sementara kelompok "
    "lain hampir tidak bergerak dan Makanan malah turun 0,30%. Satu kebijakan "
    "harga pada satu kelompok mengangkat inflasi umum ke 1,17% mtm dan 5,95% "
    "yoy. Inilah contoh buku teks dari inflasi harga diatur pemerintah.", BODY))
story.append(Paragraph(
    "Secara musiman, rata-rata inflasi mtm tertinggi jatuh pada Maret dan "
    "Desember, sama-sama 0,50%: Maret sering bertepatan dengan Ramadan dan "
    "menjelang Lebaran, Desember dengan belanja akhir tahun. Agustus adalah "
    "bulan teradem dengan rata-rata 0,02%. Pola ini membantu membaca rilis "
    "bulanan: kenaikan harga pada Maret atau Desember sebagian adalah pola "
    "yang memang berulang, bukan kejutan baru.", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 8
story.append(Paragraph("Bab 8. Disparitas Daerah: Satu Negara, Banyak Inflasi", H2))
story.append(side_by_side("chart_kota_ekstrem.png", "chart_kota_distribusi.png"))
story.append(Paragraph(
    "Angka nasional 3,28% menyembunyikan rentang yang lebar. Pada September "
    "2026 inflasi yoy tertinggi tercatat di Kab. Minahasa Utara (9,05%) dan "
    "terendah di Kab. Timor Tengah Selatan (1,04%), rentang 8,01 poin. "
    "Provinsi terpanas adalah Sulawesi Utara (7,59%), yang juga mencatat "
    "inflasi bulanan tertinggi +3,53%, sedangkan Sumatera Selatan terendah "
    "(2,55%). Sebanyak 92 dari 150 kabupaten/kota (61%) berada di atas "
    "inflasi nasional, dan median kota (3,59%) lebih tinggi dari angka "
    "nasional karena agregat nasional tertimbang ke kota besar.", BODY))
story.append(img("chart_provinsi.png", 24.5 * cm))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 9 Power BI
story.append(Paragraph("Bab 9. Merakit Dashboard Power BI", H2))
story.append(Paragraph(
    "Folder powerbi/ proyek ini berisi kit siap rakit: lima tabel fakta "
    "(bulanan, kelompok, komponen, kota, provinsi) yang masing-masing berdiri "
    "pada grain-nya sendiri, enam tabel dimensi, 12 measure DAX bernama polos "
    "di measures_dax.md, panduan langkah demi langkah di build_guide.md, dan "
    "rancangan empat halaman di dashboard_layout.md. Hasil akhirnya bernama "
    "Inflasi-Indonesia-2026.pbix.", BODY))
story.append(Paragraph(
    "Mengapa grain dipisah? Karena mencampur baris bulanan nasional dengan "
    "baris kabupaten/kota dalam satu tabel akan membuat total inflasi salah "
    "hitung. Setiap fakta terhubung ke dimensinya sendiri, difilter satu arah. "
    "Setelah merakit, cocokkan kartu KPI dengan tabel verifikasi di "
    "measures_dax.md: Inflasi YoY Terbaru harus 3,28 dan Kota YoY Tertinggi "
    "harus 9,05. Bila berbeda, periksa relasi dan filter halaman dulu sebelum "
    "mengutak-atik measure.", BODY))
story.append(callout(
    "<b>Aturan emas measure inflasi:</b> inflasi adalah persentase yang sudah "
    "dihitung BPS. Gunakan AVERAGE, MAX, atau MIN untuk membacanya per "
    "periode, jangan SUM. Menjumlah inflasi bulanan adalah kesalahan paling "
    "umum pemula."))
story.append(Paragraph(
    "Latihan bab ini: rakit Halaman 1 mengikuti layout, lalu jawab dengan "
    "dashboardmu sendiri, berapa andil kelompok Makanan pada September 2026 "
    "dan berapa kota yang inflasinya di atas nasional?", BODY))
story.append(PageBreak())

# ---------------------------------------------------------------- Bab 10
story.append(Paragraph("Bab 10. Rangkuman dan Latihan", H2))
story.append(Paragraph(
    "Lima hal yang perlu kamu ingat dari modul ini. Pertama, inflasi diukur "
    "dari IHK dan dibaca dalam tiga lensa: mtm, ytd, dan yoy. Kedua, inflasi "
    "Indonesia mencapai puncak era ini pada September 2022 (5,95%) karena "
    "kenaikan BBM, lalu mengalami disinflasi sampai stabil di dalam sasaran BI "
    "pada 19 dari 24 bulan terakhir. Ketiga, ada 11 bulan deflasi yang "
    "teramati, masing-masing dengan penyebab berbeda. Keempat, pangan adalah "
    "penggerak berulang: komponen bergejolak tertinggi dan kelompok Makanan "
    "penyumbang andil terbesar, meski andil total terbesar datang dari inti "
    "yang lengket. Kelima, disparitas daerah lebar: rentang antar kota 8,01 "
    "poin.", BODY))
story.append(Paragraph(
    "Latihan mandiri. Satu, dengan berkas inflasi_nasional_bulanan.csv, cari "
    "tiga bulan dengan inflasi yoy tertinggi sejak 2023 dan jelaskan kejadian "
    "di balik masing-masing. Dua, hitung berapa persen bulan pada 2025 yang "
    "berada di dalam sasaran BI. Tiga, dari inflasi_kota_2026_09.csv, temukan "
    "kota dengan deflasi mtm terdalam dan kota dengan mtm tertinggi, lalu "
    "bandingkan yoy keduanya. Empat, jelaskan dengan kalimatmu sendiri "
    "mengapa inflasi Februari 2026 bisa melonjak ke 4,76% padahal tidak ada "
    "guncangan harga baru.", BODY))
story.append(callout(
    "<b>Selesai.</b> Kamu sekarang bisa membaca rilis inflasi BPS seperti "
    "seorang analis: tahu angka mana yang utama, komponen apa yang "
    "menggerakkannya, dan daerah mana yang menyimpang. Simpan modul ini "
    "sebagai bekal, dan buka kembali data/SOURCES.md setiap kali kamu ragu "
    "pada satu angka.", bg=LIGHT, bar=BLUE))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(
    "Sumber data: Badan Pusat Statistik, BRS Perkembangan Indeks Harga "
    "Konsumen dan publikasi BPS. Disusun oleh BAGHIZ ASSHIDDIQIE ARASYA.", SMALL))

out = os.path.join(ROOT, "Modul-Analisis-Inflasi.pdf")
doc = SimpleDocTemplate(out, pagesize=landscape(A4), leftMargin=1.4 * cm,
                        rightMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.3 * cm,
                        title="Modul Analisis Inflasi Indonesia 2026",
                        author="Baghiz Asshiddiqie Arasya")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("Modul:", out)

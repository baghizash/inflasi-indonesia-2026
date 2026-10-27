# -*- coding: utf-8 -*-
"""
Parser BRS "Perkembangan Indeks Harga Konsumen" format baru (2022=100).

Mengekstrak dari teks hasil pdftotext -layout:
  - Tabel 1 : IHK + inflasi mtm/ytd/yoy + andil per kelompok pengeluaran (12 baris: Umum + 11 kelompok)
  - Tabel 9 : komponen (Umum, Inti, Harga Diatur Pemerintah, Bergejolak, Energi, Bahan Makanan)
  - Tabel 3-7: provinsi (IHK, yoy, mtm)
  - Tabel 8 : kabupaten/kota (IHK, yoy, mtm)

Output JSON per PDF ke data/raw_parsed/<nama>.json
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "research")
OUT = os.path.join(ROOT, "data", "raw_parsed")
os.makedirs(OUT, exist_ok=True)

NUM = r"-?\d+,\d{2}|~0"
NUMRE = re.compile(NUM)


def num(s):
    if s is None:
        return None
    s = s.strip()
    if s == "~0":
        return 0.0
    return float(s.replace(".", "").replace(",", ".")) if s.count(",") else float(s.replace(",", "."))


def get_text(pdf):
    txt = os.path.join(RES, os.path.basename(pdf).replace(".pdf", ".txt"))
    if not os.path.exists(txt):
        subprocess.run(["pdftotext", "-layout", pdf, txt], check=True)
    with open(txt, encoding="utf-8", errors="replace") as f:
        return f.read()


def region(text, start_pat, end_pats):
    m = re.search(start_pat, text)
    if not m:
        return ""
    start = m.start()
    end = len(text)
    for p in end_pats:
        m2 = re.search(p, text[start + 10:])
        if m2:
            end = min(end, start + 10 + m2.start())
    return text[start:end]


KELOMPOK_ORDER = [
    "Umum",
    "Makanan, Minuman dan Tembakau",
    "Pakaian dan Alas Kaki",
    "Perumahan, Air, Listrik, dan Bahan Bakar Rumah Tangga",
    "Perlengkapan, Peralatan, dan Pemeliharaan Rutin Rumah Tangga",
    "Kesehatan",
    "Transportasi",
    "Informasi, Komunikasi, dan Jasa Keuangan",
    "Rekreasi, Olahraga, dan Budaya",
    "Pendidikan",
    "Penyediaan Makanan dan Minuman/Restoran",
    "Perawatan Pribadi dan Jasa Lainnya",
]

KOMPONEN_ORDER = [
    "Umum",
    "Inti",
    "Harga Diatur Pemerintah",
    "Bergejolak",
    "Energi",
    "Bahan Makanan",
]


def parse_rate_table(text, start_pat, order, ncols=8):
    """Tabel 1 / Tabel 9: baris data = baris teks yang memuat tepat ncols angka.
    Nama kelompok bisa membungkus 2 baris; urutan baris mengikuti urutan resmi BPS."""
    reg = region(text, start_pat, [r"\n\s*Tabel\s+\d", r"\n\s*\d+\.\s+Indeks Harga"])
    rows = []
    for line in reg.splitlines():
        vals = NUMRE.findall(line)
        # baris data punya ncols angka dan setidaknya 3 di antaranya indeks > 90
        if len(vals) == ncols:
            rows.append([num(v) for v in vals])
    if len(rows) != len(order):
        print(f"  PERINGATAN: ditemukan {len(rows)} baris, diharapkan {len(order)}")
    out = []
    for name, vals in zip(order, rows):
        out.append({"nama": name, "nilai": vals})
    return out


ENTRY_START = re.compile(r"(?<!\d)(\d{1,3})\.\s*([A-Z][A-Za-z\.\s/'-]*?)\d?(?=\s{2,}|\n|$)")
TRIPLE = re.compile(r"(\d{2,3},\d{2})\s+(-?\d+,\d{2})\s+(-?\d+,\d{2})")


def parse_geo_region(reg):
    """Parse baris-per-baris: setiap baris memuat 1-2 entri bernomor.
    Angka (IHK, yoy, mtm) ada di baris yang sama dalam rentang kolom entri,
    atau di baris berikutnya pada rentang kolom yang sama (nama terbungkus)."""
    lines = reg.splitlines()
    results = []
    for li, line in enumerate(lines):
        starts = [(m.start(), int(m.group(1)),
                   re.sub(r"\d+$", "", re.sub(r"\s+", " ", m.group(2))).strip())
                  for m in ENTRY_START.finditer(line)]
        for si, (pos, no, name) in enumerate(starts):
            if len(name) < 3:
                continue
            end = starts[si + 1][0] if si + 1 < len(starts) else max(len(line), 80)
            seg = line[pos:end]
            t = TRIPLE.search(seg)
            if not t:
                for lj in (li + 1, li + 2):
                    if lj < len(lines):
                        seg2 = lines[lj][max(0, pos - 3):end if si + 1 < len(starts) else len(lines[lj])]
                        t = TRIPLE.search(seg2)
                        if t:
                            break
            if t:
                results.append({"no": no, "nama": name,
                                "ihk": num(t.group(1)), "yoy": num(t.group(2)),
                                "mtm": num(t.group(3))})
    return results


PROVINSI_38 = [
    "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan",
    "Bengkulu", "Lampung", "Kep. Bangka Belitung", "Kepulauan Riau", "DKI Jakarta",
    "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten", "Bali",
    "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat", "Kalimantan Tengah",
    "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara", "Sulawesi Utara",
    "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara", "Gorontalo",
    "Sulawesi Barat", "Maluku", "Maluku Utara", "Papua Barat", "Papua Barat Daya",
    "Papua", "Papua Selatan", "Papua Tengah", "Papua Pegunungan",
]


def parse_geo_table(text):
    """Tabel 3-7 (provinsi) dan Tabel 8 (kab/kota per kelompok pulau, penomoran
    lokal per kelompok). Parse seluruh rentang tabel, klasifikasikan via daftar
    38 provinsi; sisanya = kab/kota, dedupe berdasarkan nama."""
    reg = region(text, r"Tabel 3\s+Perbandingan IHK", ["\x0c\\s*Tabel 9\\s"])
    entries = parse_geo_region(reg)
    prov, kota, seen = [], [], set()
    for e in entries:
        if e["nama"] in PROVINSI_38:
            if e["nama"] not in seen:
                prov.append(e)
                seen.add(e["nama"])
        elif e["nama"] not in seen and e["nama"] != "NASIONAL":
            kota.append(e)
            seen.add(e["nama"])
    return prov, kota


def main():
    for pdf, tag in [("brs_2026_09.pdf", "2026-09"), ("brs_202511.pdf", "2025-11"),
                     ("brs_202602.pdf", "2026-02")]:
        path = os.path.join(RES, pdf)
        if not os.path.exists(path):
            print("lewati (tidak ada):", pdf)
            continue
        text = get_text(path)
        data = {"periode": tag}
        t1 = parse_rate_table(text, r"Tabel 1\s+IHK dan Tingkat Inflasi", KELOMPOK_ORDER)
        data["tabel1_kelompok"] = t1
        print(tag, "Tabel 1:", len(t1), "baris")
        t9 = parse_rate_table(text, r"Tabel 9\s+Tingkat Inflasi", KOMPONEN_ORDER)
        data["tabel9_komponen"] = t9
        print(tag, "Tabel 9:", len(t9), "baris")
        if tag == "2026-09":
            prov, kota = parse_geo_table(text)
            data["provinsi"] = prov
            data["kota"] = kota
            print(tag, "provinsi:", len(prov), "| kota:", len(kota))
        with open(os.path.join(OUT, f"brs_{tag}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

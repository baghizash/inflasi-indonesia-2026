# Measure DAX: Inflasi Indonesia 2026

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
| Inflasi YoY Terbaru (Sep 2026) | 3,28 | fact_inflasi_bulanan, bulan_key 202609 |
| Inflasi MtM Terbaru (Sep 2026) | 0,30 | fact_inflasi_bulanan, bulan_key 202609 |
| IHK Terbaru (Sep 2026, 2022=100) | 112,31 | fact_inflasi_bulanan, bulan_key 202609 |
| Inflasi YoY Tertinggi pada seri | 5,95 | MAX fact_inflasi_bulanan (Sep 2022) |
| Jumlah Bulan Deflasi (mtm terisi) | 11 | COUNT fact_inflasi_bulanan mtm < 0 |
| Kota YoY Tertinggi (Sep 2026) | 9,05 | MAX fact_inflasi_kota (Kab. Minahasa Utara) |
| Kota YoY Terendah (Sep 2026) | 1,04 | MIN fact_inflasi_kota (Kab. Timor Tengah Selatan) |
| Kota di Atas YoY Nasional | 92 | COUNT fact_inflasi_kota yoy > 3,28 |
| Andil YoY Kelompok Terbesar (Sep 2026) | 1,28 | MAX fact_inflasi_kelompok (Makanan) |

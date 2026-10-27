#!/usr/bin/env python3
"""Build the InflasiIndonesia2026 PBIP package (validated pattern, cf. IPMIndonesia2026).

Output: ~/workspace/inflasi/pbip/InflasiIndonesia2026/ + copy at ~/workspace/pbip/InflasiIndonesia2026/
Validate: python3 ~/workspace/pbip/validate_pbip.py ~/workspace/inflasi/pbip/InflasiIndonesia2026
"""
import json, uuid, shutil
from pathlib import Path

NS = uuid.UUID('7a2d91c4-5e6f-4a8b-9c01-2d3e4f5a6b70')
def G(s): return str(uuid.uuid5(NS, s))

PROJ = 'InflasiIndonesia2026'
PROOT = Path(__file__).resolve().parent.parent
ROOT = PROOT / 'pbip' / PROJ
KIT = PROOT / 'powerbi'
REP = ROOT / f'{PROJ}.Report'
SEM = ROOT / f'{PROJ}.SemanticModel'
DEF_R = REP / 'definition'
DEF_S = SEM / 'definition'

VC = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json'
PG = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json'

def W(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
def WJ(path, obj):
    W(path, json.dumps(obj, indent=2, ensure_ascii=False))

# ---------------------------------------------------------------- field refs
def col(e, p):  return {"Column": {"Expression": {"SourceRef": {"Entity": e}}, "Property": p}}
def mea(e, p):  return {"Measure": {"Expression": {"SourceRef": {"Entity": e}}, "Property": p}}
def agg(e, p, f=0): return {"Aggregation": {"Expression": {"SourceRef": {"Entity": e}}, "Function": f, "Property": p}}
def proj(field, e, p, native=None):
    return {"field": field, "queryRef": f"{e}.{p}", "nativeQueryRef": native or p}
def sortby(field, direction):
    return {"field": field, "direction": direction}

_fc = [0]
def catfilter(alias, e, p, values, numeric=False):
    _fc[0] += 1
    return {
        "name": f"flt{_fc[0]:014x}",
        "ordinal": _fc[0],
        "field": col(e, p),
        "type": "Categorical",
        "filter": {
            "Version": 2,
            "From": [{"Name": alias, "Entity": e, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": p}}],
                "Values": [[{"Literal": {"Value": f"'{v}'" if not numeric else f"{v}"}}] for v in values],
            }}}],
        },
        "isHiddenInViewMode": False,
        "isLockedInViewMode": False,
    }

def title_obj(text):
    return {"title": [{"properties": {
        "show": {"expr": {"Literal": {"Value": "true"}}},
        "text": {"expr": {"Literal": {"Value": f"'{text}'"}}},
        "bold": {"expr": {"Literal": {"Value": "true"}}},
    }}]}

def visual(name, x, y, w, h, vtype, qstate=None, title_text=None, filters=None,
           sorts=None, objects=None, z=0):
    v = {"$schema": VC, "name": name,
         "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
         "visual": {"visualType": vtype}}
    if qstate is not None:
        q = {"queryState": qstate}
        if sorts:
            q["sortDefinition"] = {"sort": sorts, "isDefaultSort": False}
        v["visual"]["query"] = q
    if objects is not None:
        v["visual"]["objects"] = objects
    if title_text:
        v["visual"]["visualContainerObjects"] = title_obj(title_text)
    if filters:
        v["filterConfig"] = {"filters": filters}
    return v

def textbox(name, x, y, w, h, text, size=14, bold=False, z=0):
    tr = {"value": text, "textStyle": {"fontFamily": "Segoe UI", "fontSize": size}}
    if bold:
        tr["textStyle"]["bold"] = True
    objects = {"general": [{"properties": {"paragraphs": [{
        "textRuns": [tr], "horizontalTextAlignment": "left"}]}}]}
    return visual(name, x, y, w, h, "textbox", objects=objects, z=z)

def slicer(name, x, y, w, h, e, p, z=0):
    return visual(name, x, y, w, h, "slicer",
                  qstate={"Values": {"projections": [proj(col(e, p), e, p)]}}, z=z)

# ------------------------------------------------------------------- TMDL
D2 = '0.00'
TABLES = {
    'dim_bulan': [
        ('bulan_key', 'int64', '0'), ('periode', 'string', None),
        ('tahun', 'int64', '0'), ('bulan', 'int64', '0'),
        ('nama_bulan', 'string', None), ('label', 'string', None)],
    'dim_tahun': [
        ('tahun_id', 'int64', '0'), ('tahun', 'int64', '0')],
    'dim_kelompok': [
        ('kelompok_id', 'int64', '0'), ('kelompok', 'string', None)],
    'dim_komponen': [
        ('komponen_id', 'int64', '0'), ('komponen', 'string', None)],
    'dim_kota': [
        ('kota_id', 'int64', '0'), ('kabupaten_kota', 'string', None)],
    'dim_provinsi': [
        ('provinsi_id', 'int64', '0'), ('provinsi', 'string', None)],
    'fact_inflasi_bulanan': [
        ('bulan_key', 'int64', '0'), ('tahun_id', 'int64', '0'),
        ('ihk', 'double', D2), ('mtm_persen', 'double', D2),
        ('ytd_persen', 'double', D2), ('yoy_persen', 'double', D2)],
    'fact_inflasi_kelompok': [
        ('bulan_key', 'int64', '0'), ('kelompok_id', 'int64', '0'),
        ('ihk', 'double', D2), ('mtm_persen', 'double', D2),
        ('ytd_persen', 'double', D2), ('yoy_persen', 'double', D2),
        ('andil_mtm', 'double', D2), ('andil_yoy', 'double', D2)],
    'fact_inflasi_komponen': [
        ('bulan_key', 'int64', '0'), ('komponen_id', 'int64', '0'),
        ('ihk', 'double', D2), ('mtm_persen', 'double', D2),
        ('ytd_persen', 'double', D2), ('yoy_persen', 'double', D2),
        ('andil_mtm', 'double', D2), ('andil_yoy', 'double', D2)],
    'fact_inflasi_kota': [
        ('kota_id', 'int64', '0'), ('bulan_key', 'int64', '0'),
        ('ihk', 'double', D2), ('yoy_persen', 'double', D2), ('mtm_persen', 'double', D2)],
    'fact_inflasi_provinsi': [
        ('provinsi_id', 'int64', '0'), ('bulan_key', 'int64', '0'),
        ('ihk', 'double', D2), ('yoy_persen', 'double', D2), ('mtm_persen', 'double', D2)],
}
SORTBY = {('dim_bulan', 'label'): 'bulan_key', ('dim_bulan', 'periode'): 'bulan_key'}
MTYPE = {'int64': 'Int64.Type', 'double': 'type number', 'string': 'type text', 'dateTime': 'type date'}

TERBARU_YOY = ('VAR KunciTerbaru =\n'
               '    MAX ( fact_inflasi_bulanan[bulan_key] )\n'
               'RETURN\n'
               '    CALCULATE ( [Inflasi YoY], fact_inflasi_bulanan[bulan_key] = KunciTerbaru )')
TERBARU_MTM = ('VAR KunciTerbaru =\n'
               '    MAX ( fact_inflasi_bulanan[bulan_key] )\n'
               'RETURN\n'
               '    CALCULATE ( [Inflasi MtM], fact_inflasi_bulanan[bulan_key] = KunciTerbaru )')
TERBARU_IHK = ('VAR KunciTerbaru =\n'
               '    MAX ( fact_inflasi_bulanan[bulan_key] )\n'
               'RETURN\n'
               '    CALCULATE ( [IHK], fact_inflasi_bulanan[bulan_key] = KunciTerbaru )')
KOTA_DI_ATAS = ('VAR Nasional = [Inflasi YoY Terbaru]\n'
                'RETURN\n'
                '    CALCULATE (\n'
                '        COUNTROWS ( fact_inflasi_kota ),\n'
                '        fact_inflasi_kota[yoy_persen] > Nasional\n'
                '    )')

MEASURES = {
    'fact_inflasi_bulanan': [
        ('Inflasi YoY', 'AVERAGE ( fact_inflasi_bulanan[yoy_persen] )', D2),
        ('Inflasi MtM', 'AVERAGE ( fact_inflasi_bulanan[mtm_persen] )', D2),
        ('IHK', 'AVERAGE ( fact_inflasi_bulanan[ihk] )', D2),
        ('Inflasi YoY Terbaru', TERBARU_YOY, D2),
        ('Inflasi MtM Terbaru', TERBARU_MTM, D2),
        ('IHK Terbaru', TERBARU_IHK, D2),
        ('Puncak Inflasi YoY', 'MAX ( fact_inflasi_bulanan[yoy_persen] )', D2),
        ('Jumlah Bulan Deflasi', 'CALCULATE ( COUNTROWS ( fact_inflasi_bulanan ), fact_inflasi_bulanan[mtm_persen] < 0 )', '0'),
    ],
    'fact_inflasi_kelompok': [
        ('Inflasi YoY Kelompok', 'AVERAGE ( fact_inflasi_kelompok[yoy_persen] )', D2),
        ('Andil YoY Kelompok', 'AVERAGE ( fact_inflasi_kelompok[andil_yoy] )', D2),
    ],
    'fact_inflasi_komponen': [
        ('Inflasi YoY Komponen', 'AVERAGE ( fact_inflasi_komponen[yoy_persen] )', D2),
        ('Andil YoY Komponen', 'AVERAGE ( fact_inflasi_komponen[andil_yoy] )', D2),
    ],
    'fact_inflasi_kota': [
        ('Kota YoY Tertinggi', 'MAX ( fact_inflasi_kota[yoy_persen] )', D2),
        ('Kota YoY Terendah', 'MIN ( fact_inflasi_kota[yoy_persen] )', D2),
        ('Jumlah Kota Di Atas Nasional', KOTA_DI_ATAS, '0'),
    ],
    'fact_inflasi_provinsi': [
        ('Provinsi YoY Tertinggi', 'MAX ( fact_inflasi_provinsi[yoy_persen] )', D2),
        ('Inflasi YoY Wilayah', 'AVERAGE ( fact_inflasi_provinsi[yoy_persen] )', D2),
    ],
}

RELATIONSHIPS = [
    ('fact_inflasi_bulanan', 'bulan_key', 'dim_bulan', 'bulan_key'),
    ('fact_inflasi_bulanan', 'tahun_id', 'dim_tahun', 'tahun_id'),
    ('fact_inflasi_kelompok', 'bulan_key', 'dim_bulan', 'bulan_key'),
    ('fact_inflasi_kelompok', 'kelompok_id', 'dim_kelompok', 'kelompok_id'),
    ('fact_inflasi_komponen', 'bulan_key', 'dim_bulan', 'bulan_key'),
    ('fact_inflasi_komponen', 'komponen_id', 'dim_komponen', 'komponen_id'),
    ('fact_inflasi_kota', 'kota_id', 'dim_kota', 'kota_id'),
    ('fact_inflasi_kota', 'bulan_key', 'dim_bulan', 'bulan_key'),
    ('fact_inflasi_provinsi', 'provinsi_id', 'dim_provinsi', 'provinsi_id'),
    ('fact_inflasi_provinsi', 'bulan_key', 'dim_bulan', 'bulan_key'),
]

def table_tmdl(name):
    cols = TABLES[name]
    out = [f'table {name}', f'\tlineageTag: {G("tab-" + name)}', '']
    for mname, dax, fmt in MEASURES.get(name, []):
        if '\n' in dax:
            body = '\n'.join('\t\t\t' + ln for ln in dax.split('\n'))
            out.append(f"\tmeasure '{mname}' = ```")
            out.append(body)
            out.append('\t\t\t```')
        else:
            out.append(f"\tmeasure '{mname}' =")
            out.append(f'\t\t\t{dax}')
        out.append(f'\t\tformatString: {fmt}')
        out.append(f'\t\tlineageTag: {G("mea-" + name + "-" + mname)}')
        out.append('')
    for cname, dtype, fmt in cols:
        out.append(f'\tcolumn {cname}')
        out.append(f'\t\tdataType: {dtype}')
        if fmt:
            out.append(f'\t\tformatString: {fmt}')
        out.append(f'\t\tlineageTag: {G("col-" + name + "-" + cname)}')
        if (name, cname) in SORTBY:
            out.append(f'\t\tsortByColumn: {SORTBY[(name, cname)]}')
        out.append('\t\tsummarizeBy: none')
        out.append(f'\t\tsourceColumn: {cname}')
        out.append('')
    pairs = ', '.join(f'{{"{c}", {MTYPE[t]}}}' for c, t, _ in cols)
    out.append(f'\tpartition {name} = m')
    out.append('\t\tmode: import')
    out.append('\t\tsource = ```')
    out.append('\t\t\t\tlet')
    out.append(f'\t\t\t\t\tSource = Csv.Document(File.Contents(FolderData & "\\{name}.csv"), [Delimiter = ",", Columns = {len(cols)}, Encoding = 65001, QuoteStyle = QuoteStyle.None]),')
    out.append('\t\t\t\t\tPromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),')
    out.append(f'\t\t\t\t\tChangedType = Table.TransformColumnTypes(PromotedHeaders, {{{pairs}}})')
    out.append('\t\t\t\tin')
    out.append('\t\t\t\t\tChangedType')
    out.append('\t\t\t\t```')
    return '\n'.join(out) + '\n'

def build_model():
    WJ(SEM / '.platform', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/platform/platformProperties/1.0.0/schema.json",
        "metadata": {"type": "SemanticModel", "displayName": PROJ},
        "config": {"version": "2.0", "logicalId": G('platform-sem')}})
    WJ(SEM / 'definition.pbism', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "settings": {}})
    W(DEF_S / 'database.tmdl', 'database\n\tcompatibilityLevel: 1600\n')
    refs = '\n'.join(f'ref table {t}' for t in TABLES)
    W(DEF_S / 'model.tmdl',
      f'model Model\n\tculture: en-US\n\tdataAccessOptions\n\t\tlegacyRedirects\n\t\treturnErrorValuesAsNull\n\n{refs}\n\nref expression FolderData\n')
    W(DEF_S / 'expressions.tmdl',
      'expression FolderData = ```\n'
      '\t\t"C:\\\\PowerBI\\\\Inflasi\\\\data" meta [IsParameterQuery = true, IsParameterQueryRequired = true, Type = "Text"]\n'
      '\t\t```\n'
      f'\tlineageTag: {G("expr-FolderData")}\n')
    rel = []
    for i, (ft, fc, tt, tc) in enumerate(RELATIONSHIPS):
        rel.append(f'relationship {G("rel-" + str(i))}')
        rel.append(f'\tfromColumn: {ft}.{fc}')
        rel.append(f'\ttoColumn: {tt}.{tc}')
        rel.append('\tcrossFilteringBehavior: oneDirection')
        rel.append('')
    W(DEF_S / 'relationships.tmdl', '\n'.join(rel))
    for t in TABLES:
        W(DEF_S / 'tables' / f'{t}.tmdl', table_tmdl(t))
    nodes = []
    for i, t in enumerate(TABLES):
        nodes.append({"location": {"x": (i % 3) * 300, "y": (i // 3) * 260},
                      "nodeIndex": t, "nodeLineageTag": G('tab-' + t),
                      "size": {"height": 200, "width": 234}, "zIndex": i})
    WJ(SEM / 'diagramLayout.json', {
        "version": "1.1.0",
        "diagrams": [{"ordinal": 0, "scrollPosition": {"x": 0, "y": 0}, "nodes": nodes,
                      "name": "All tables", "zoomValue": 100, "pinKeyFields": [],
                      "showExtraHeaderInfo": False, "hideKeyFieldsWhenCollapsed": False}],
        "selectedDiagram": "All tables", "defaultDiagram": "All tables"})

# ------------------------------------------------------------------ report
FB = 'fact_inflasi_bulanan'; FKEL = 'fact_inflasi_kelompok'; FKOM = 'fact_inflasi_komponen'
FK = 'fact_inflasi_kota'; FP = 'fact_inflasi_provinsi'
DB = 'dim_bulan'; DTH = 'dim_tahun'; DKEL = 'dim_kelompok'; DKOM = 'dim_komponen'
DK = 'dim_kota'; DPV = 'dim_provinsi'
SEP26 = lambda a='db': catfilter(a, DB, 'bulan_key', [202609], numeric=True)
DES = lambda a='db2': catfilter(a, DB, 'bulan', [12], numeric=True)

def build_report():
    WJ(REP / '.platform', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/platform/platformProperties/1.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": PROJ},
        "config": {"version": "2.0", "logicalId": G('platform-rep')}})
    WJ(REP / 'definition.pbir', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": f"../{PROJ}.SemanticModel"}}})
    WJ(DEF_R / 'version.json', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "1.0.0"})
    WJ(DEF_R / 'report.json', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
        "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.60", "type": "SharedResources"}}})
    WJ(REP / 'StaticResources' / 'SharedResources' / 'BaseThemes' / 'CY24SU10.json', {
        "name": "CY24SU10",
        "dataColors": ["#14406B", "#D62828", "#F2C14E", "#2A9D8F", "#7FB0D9", "#26313B",
                       "#744EC2", "#D64550", "#197278", "#1AAB40", "#15C6F4", "#4092FF",
                       "#FF9B85", "#FFC36D", "#A0D8EF", "#5E4B8B"],
        "background": "#FAF6EF", "foreground": "#26313B", "tableAccent": "#14406B"})

    pages = {}

    # ---- Halaman 1: Ringkasan Inflasi
    p1 = []
    p1.append(textbox('v01Title', 0, 0, 900, 60, 'Inflasi Indonesia 2026: Ringkasan Inflasi', 20, bold=True, z=0))
    p1.append(slicer('v02SlicerPeriode', 930, 8, 330, 52, DB, 'label', z=1))
    cards = [(FB, 'Inflasi YoY Terbaru', 'Inflasi YoY Terbaru (Sep 2026)'),
             (FB, 'Inflasi MtM Terbaru', 'Inflasi MtM Terbaru (Sep 2026)'),
             (FB, 'IHK Terbaru', 'IHK Terbaru (2022=100)'),
             (FB, 'Puncak Inflasi YoY', 'Puncak YoY (Sep 2022)')]
    for i, (ent, m, t) in enumerate(cards):
        p1.append(visual(f'v{3+i:02d}Card', i * 320, 76, 300, 110, 'card',
                         qstate={"Values": {"projections": [proj(mea(ent, m), ent, m)]}},
                         title_text=t, z=2 + i))
    p1.append(visual('v07LineYoY', 0, 200, 620, 250, 'lineChart',
                     qstate={"Category": {"projections": [proj(col(DB, 'label'), DB, 'label')]},
                             "Y": {"projections": [proj(mea(FB, 'Inflasi YoY'), FB, 'Inflasi YoY')]}},
                     title_text='Tren Inflasi YoY (sasaran BI 1,5% sampai 3,5%)',
                     sorts=[sortby(col(DB, 'bulan_key'), 'Ascending')], z=6))
    p1.append(visual('v08BarAndilKel', 640, 200, 620, 250, 'clusteredBarChart',
                     qstate={"Category": {"projections": [proj(col(DKEL, 'kelompok'), DKEL, 'kelompok')]},
                             "Y": {"projections": [proj(mea(FKEL, 'Andil YoY Kelompok'), FKEL, 'Andil YoY Kelompok')]}},
                     title_text='Andil YoY per Kelompok, Sep 2026 (Makanan 1,28)',
                     filters=[SEP26()],
                     sorts=[sortby(mea(FKEL, 'Andil YoY Kelompok'), 'Descending')], z=7))
    p1.append(textbox('v09Metode', 0, 466, 1260, 60,
                      'Sumber: BPS, BRS Perkembangan Indeks Harga Konsumen. Seri nasional Januari 2019 sampai September 2026. Sasaran inflasi Bank Indonesia 2,5% plus minus 1%; 19 dari 24 bulan terakhir berada di dalam sasaran.', 12, z=8))
    pages['pg01Ringkasan'] = ('Ringkasan Inflasi', p1)

    # ---- Halaman 2: Komponen dan Kelompok
    p2 = []
    p2.append(textbox('v01Title', 0, 0, 900, 60, 'Komponen dan Kelompok Pengeluaran', 20, bold=True, z=0))
    p2.append(slicer('v02SlicerPeriode', 930, 8, 330, 52, DB, 'label', z=1))
    p2.append(visual('v03BarKompYoY', 0, 76, 620, 260, 'clusteredBarChart',
                     qstate={"Category": {"projections": [proj(col(DKOM, 'komponen'), DKOM, 'komponen')]},
                             "Y": {"projections": [proj(mea(FKOM, 'Inflasi YoY Komponen'), FKOM, 'Inflasi YoY Komponen')]}},
                     title_text='Inflasi YoY per Komponen, Sep 2026 (Bergejolak 5,03)',
                     filters=[SEP26()],
                     sorts=[sortby(mea(FKOM, 'Inflasi YoY Komponen'), 'Descending')], z=2))
    p2.append(visual('v04BarKompAndil', 640, 76, 620, 260, 'clusteredBarChart',
                     qstate={"Category": {"projections": [proj(col(DKOM, 'komponen'), DKOM, 'komponen')]},
                             "Y": {"projections": [proj(mea(FKOM, 'Andil YoY Komponen'), FKOM, 'Andil YoY Komponen')]}},
                     title_text='Andil YoY per Komponen, Sep 2026 (Inti 1,82)',
                     filters=[SEP26()],
                     sorts=[sortby(mea(FKOM, 'Andil YoY Komponen'), 'Descending')], z=3))
    p2.append(visual('v05BarKelYoY', 0, 352, 620, 308, 'clusteredBarChart',
                     qstate={"Category": {"projections": [proj(col(DKEL, 'kelompok'), DKEL, 'kelompok')]},
                             "Y": {"projections": [proj(mea(FKEL, 'Inflasi YoY Kelompok'), FKEL, 'Inflasi YoY Kelompok')]}},
                     title_text='Inflasi YoY 11 Kelompok, Sep 2026',
                     filters=[SEP26()],
                     sorts=[sortby(mea(FKEL, 'Inflasi YoY Kelompok'), 'Descending')], z=4))
    p2.append(visual('v06TableKel', 640, 352, 620, 308, 'tableEx',
                     qstate={"Values": {"projections": [
                         proj(col(DB, 'label'), DB, 'label'),
                         proj(col(DKEL, 'kelompok'), DKEL, 'kelompok'),
                         proj(agg(FKEL, 'mtm_persen', 1), FKEL, 'mtm_persen', 'Average of mtm_persen'),
                         proj(agg(FKEL, 'yoy_persen', 1), FKEL, 'yoy_persen', 'Average of yoy_persen'),
                         proj(agg(FKEL, 'andil_yoy', 1), FKEL, 'andil_yoy', 'Average of andil_yoy')]}},
                     title_text='Tabel Kelompok: Nov 2025, Feb 2026, Sep 2026',
                     sorts=[sortby(agg(FKEL, 'andil_yoy', 1), 'Descending')], z=5))
    pages['pg02KomponenKelompok'] = ('Komponen & Kelompok', p2)

    # ---- Halaman 3: Peta Harga per Wilayah
    p3 = []
    p3.append(textbox('v01Title', 0, 0, 900, 60, 'Peta Harga per Wilayah, September 2026', 20, bold=True, z=0))
    cards3 = [(FK, 'Kota YoY Tertinggi', 'Kota Tertinggi (Minahasa Utara)'),
              (FK, 'Kota YoY Terendah', 'Kota Terendah (Timor Tengah Selatan)'),
              (FK, 'Jumlah Kota Di Atas Nasional', 'Kota di Atas Nasional'),
              (FP, 'Provinsi YoY Tertinggi', 'Provinsi Tertinggi (Sulawesi Utara)')]
    for i, (ent, m, t) in enumerate(cards3):
        p3.append(visual(f'v{2+i:02d}Card', i * 320, 76, 300, 110, 'card',
                         qstate={"Values": {"projections": [proj(mea(ent, m), ent, m)]}},
                         title_text=t, z=1 + i))
    p3.append(visual('v06BarProv', 0, 200, 620, 460, 'clusteredBarChart',
                     qstate={"Category": {"projections": [proj(col(DPV, 'provinsi'), DPV, 'provinsi')]},
                             "Y": {"projections": [proj(mea(FP, 'Inflasi YoY Wilayah'), FP, 'Inflasi YoY Wilayah')]}},
                     title_text='Inflasi YoY 38 Provinsi, Sep 2026',
                     sorts=[sortby(mea(FP, 'Inflasi YoY Wilayah'), 'Descending')], z=5))
    p3.append(visual('v07BarKota', 640, 200, 620, 460, 'clusteredBarChart',
                     qstate={"Category": {"projections": [proj(col(DK, 'kabupaten_kota'), DK, 'kabupaten_kota')]},
                             "Y": {"projections": [proj(agg(FK, 'yoy_persen', 1), FK, 'yoy_persen', 'Average of yoy_persen')]}},
                     title_text='Inflasi YoY 150 Kab/Kota, Sep 2026 (rentang 8,01 poin)',
                     sorts=[sortby(agg(FK, 'yoy_persen', 1), 'Descending')], z=6))
    pages['pg03Wilayah'] = ('Wilayah', p3)

    # ---- Halaman 4: Sejarah dan Kemusiman
    p4 = []
    p4.append(textbox('v01Title', 0, 0, 900, 60, 'Sejarah dan Kemusiman', 20, bold=True, z=0))
    p4.append(slicer('v02SlicerTahun', 930, 8, 330, 52, DTH, 'tahun', z=1))
    p4.append(visual('v03ColMtM', 0, 76, 620, 280, 'clusteredColumnChart',
                     qstate={"Category": {"projections": [proj(col(DB, 'label'), DB, 'label')]},
                             "Y": {"projections": [proj(mea(FB, 'Inflasi MtM'), FB, 'Inflasi MtM')]}},
                     title_text='Inflasi MtM per Bulan (celah = tidak terkompilasi)',
                     sorts=[sortby(col(DB, 'bulan_key'), 'Ascending')], z=2))
    p4.append(visual('v04ColDes', 640, 76, 620, 280, 'clusteredColumnChart',
                     qstate={"Category": {"projections": [proj(col(DTH, 'tahun'), DTH, 'tahun')]},
                             "Y": {"projections": [proj(mea(FB, 'Inflasi YoY'), FB, 'Inflasi YoY')]}},
                     title_text='Inflasi Tahunan Desember per Tahun',
                     filters=[DES()], z=3))
    p4.append(visual('v05ColMusim', 0, 372, 620, 220, 'clusteredColumnChart',
                     qstate={"Category": {"projections": [proj(col(DB, 'nama_bulan'), DB, 'nama_bulan')]},
                             "Y": {"projections": [proj(mea(FB, 'Inflasi MtM'), FB, 'Inflasi MtM')]}},
                     title_text='Kemusiman: Rata-rata MtM per Bulan Kalender',
                     sorts=[sortby(col(DB, 'bulan'), 'Ascending')], z=4))
    p4.append(visual('v06CardDeflasi', 640, 372, 300, 110, 'card',
                     qstate={"Values": {"projections": [proj(mea(FB, 'Jumlah Bulan Deflasi'), FB, 'Jumlah Bulan Deflasi')]}},
                     title_text='Jumlah Bulan Deflasi Teramati', z=5))
    p4.append(textbox('v07Catatan', 960, 372, 300, 220,
                      'Puncak musiman rata-rata mtm jatuh pada Maret dan Desember (0,50%). September 2022: Transportasi naik 8,88% mtm pada bulan kenaikan BBM.', 13, z=6))
    p4.append(textbox('v08Catatan2', 640, 498, 300, 94,
                      'Deflasi terdalam: Februari 2025 minus 0,48% (diskon tarif listrik).', 12, z=7))
    pages['pg04Sejarah'] = ('Sejarah & Kemusiman', p4)

    order = list(pages)
    for pname, (disp, visuals) in pages.items():
        WJ(DEF_R / 'pages' / pname / 'page.json', {
            "$schema": PG, "name": pname, "displayName": disp,
            "displayOption": "FitToPage", "height": 720, "width": 1280})
        for v in visuals:
            WJ(DEF_R / 'pages' / pname / 'visuals' / v['name'] / 'visual.json', v)
    WJ(DEF_R / 'pages' / 'pages.json', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": order, "activePageName": order[0]})

README = """LANGKAH MEMBUKA PAKET PBIP: Inflasi Indonesia 2026
====================================================================

1. Ekstrak file ZIP ini ke folder lokal (mis. C:\\PowerBI\\Inflasi).
2. Buka file InflasiIndonesia2026.pbip dengan Power BI Desktop.
3. Saat diminta parameter, klik Edit Parameters atau Transform Data,
   lalu arahkan FolderData ke folder "data" di dalam hasil ekstrak
   (folder berisi 11 file CSV kit).
4. Klik Refresh agar seluruh tabel termuat.
5. Cek cepat angka kunci (Halaman 1: Ringkasan Inflasi):
   - Kartu Inflasi YoY Terbaru harus menunjukkan 3,28
   - Kartu Inflasi MtM Terbaru harus menunjukkan 0,30
   - Kartu IHK Terbaru harus menunjukkan 112,31 (basis 2022=100)
   - Kartu Puncak YoY harus menunjukkan 5,95 (September 2022)
   - Halaman 3: Kota YoY Tertinggi 9,05 (Kab. Minahasa Utara),
     Kota YoY Terendah 1,04 (Kab. Timor Tengah Selatan),
     Jumlah Kota Di Atas Nasional 92, Provinsi Tertinggi 7,59
   - Halaman 4: Jumlah Bulan Deflasi Teramati 11
6. Jika semua cocok, Save As menjadi Inflasi-Indonesia-2026.pbix.

Catatan sentuhan pertama (wajar terjadi):
- Slicer periode mungkin tampil sebagai daftar (list), bukan slider.
  Itu normal untuk data periode kategori.
- Visual peta tidak dipakai (diganti bar terurut) karena visual peta PBIR
  rawan error; disparitas wilayah tetap terbaca jelas dari bar.
- Inflasi adalah persentase resmi BPS: measure memakai AVERAGE, MAX,
  atau MIN, jangan pernah SUM.
- Seri mtm mempunyai celah (bulan yang tidak terkompilasi dari sumber
  resmi); grafik mtm akan menampilkan kekosongan pada bulan tersebut.
  Lihat data/SOURCES.md di repo untuk daftar lengkapnya.
"""

# --------------------------------------------------------------------- main
def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    (ROOT / 'data').mkdir(parents=True)
    for f in sorted(KIT.glob('*.csv')):
        shutil.copy(f, ROOT / 'data' / f.name)
    WJ(ROOT / f'{PROJ}.pbip', {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": f"{PROJ}.Report"}}],
        "settings": {"enableAutoRecovery": True}})
    W(ROOT / '.gitignore', '**/.pbi/localSettings.json\n**/.pbi/cache.abf\n')
    W(ROOT / 'README-LANGKAH.txt', README)
    build_model()
    build_report()
    dst = Path.home() / 'workspace' / 'pbip' / PROJ
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ROOT, dst)
    print('built', ROOT, '+ copy at', dst)

if __name__ == '__main__':
    main()

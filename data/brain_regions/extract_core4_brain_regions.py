#!/usr/bin/env python3
"""Extract only aseg+DKT.VINN.withCC.stats volumes; read-only access to source data."""
import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
DEFAULT_ROOT = Path('/mnt/sda/public/00_Datasets/public/MRI/UKbiobank/UKB_84436/T1_seg')
STEM = 'recommended_core4_i2_i3_brain_regions'
SEG_FILE = 'aseg+DKT.VINN.withCC.stats'
CORTEX = dict(zip(
    'caudalanteriorcingulate caudalmiddlefrontal cuneus entorhinal fusiform inferiorparietal '
    'inferiortemporal isthmuscingulate lateraloccipital lateralorbitofrontal lingual '
    'medialorbitofrontal middletemporal parahippocampal paracentral parsopercularis '
    'parsorbitalis parstriangularis pericalcarine postcentral posteriorcingulate precentral '
    'precuneus rostralanteriorcingulate rostralmiddlefrontal superiorfrontal superiorparietal '
    'superiortemporal supramarginal transversetemporal insula'.split(),
    '尾侧前扣带皮层 尾侧额中回 楔叶 内嗅皮层 梭状回 顶下小叶 颞下回 扣带峡部 '
    '外侧枕叶皮层 外侧眶额皮层 舌回 内侧眶额皮层 颞中回 海马旁回 中央旁小叶 '
    '额下回盖部 额下回眶部 额下回三角部 距状沟周围皮层 中央后回 后扣带皮层 '
    '中央前回 楔前叶 吻侧前扣带皮层 吻侧额中回 额上回 顶上小叶 颞上回 '
    '缘上回 横颞回 岛叶'.split()))
STRUCTURES = {
    'Cerebral-White-Matter': '大脑白质', 'Lateral-Ventricle': '侧脑室',
    'Inf-Lat-Vent': '侧脑室下角', 'Cerebellum-White-Matter': '小脑白质',
    'Cerebellum-Cortex': '小脑皮层', 'Thalamus': '丘脑', 'Caudate': '尾状核',
    'Putamen': '壳核', 'Pallidum': '苍白球', '3rd-Ventricle': '第三脑室',
    '4th-Ventricle': '第四脑室', '5th-Ventricle': '第五脑室标签（透明隔腔）',
    'Brain-Stem': '脑干', 'Hippocampus': '海马', 'Amygdala': '杏仁核',
    'CSF': '脑脊液标签区（非全颅脑脊液总量）', 'Accumbens-area': '伏隔核区',
    'VentralDC': '腹侧间脑复合区', 'choroid-plexus': '脉络丛', 'vessel': '血管标签区',
    'WM-hypointensities': '白质低信号标签区',
    'non-WM-hypointensities': '非白质低信号标签区', 'Optic-Chiasm': '视交叉',
    'UnsegmentedWhiteMatter': '未归入皮层分区的白质',
    'CC_Posterior': '胼胝体后部', 'CC_Mid_Posterior': '胼胝体中后部',
    'CC_Central': '胼胝体中央部', 'CC_Mid_Anterior': '胼胝体中前部',
    'CC_Anterior': '胼胝体前部',
}
GLOBAL = {
    'SubCortGrayVol': '皮层下灰质总体积', 'MaskVol': '脑掩膜体积（不是颅内容积）',
    'BrainSegVol': '脑分割总体积', 'BrainSegVolNotVent': '排除脑室后的脑分割体积',
    'SupraTentorialVol': '幕上总体积', 'SupraTentorialVolNotVent': '排除脑室后的幕上体积',
    'lhCerebralWhiteMatterVol': '左侧大脑白质总体积',
    'rhCerebralWhiteMatterVol': '右侧大脑白质总体积',
    'CerebralWhiteMatterVol': '双侧大脑白质总体积',

}
META = {
    'IID': ('文本', '原始名单的受试者 ID；必须作为字符串读取'),
    'instance': ('访视编码', '2=首次影像访视，3=重复影像访视；同一 IID 两行'),
    'age': ('年', '名单中的访视年龄，逐行原样保留；空值不插补'),
    'sex': ('编码', '名单中的 sex，0=女性、1=男性；原样保留'),
    'cohort_mri_path': ('路径', '名单中的 T1_rigid 路径，仅用于匹配溯源，不是本次统计输入'),
    'segmentation_input_path': ('路径', '_pipeline/provenance.json 记录的实际分割输入路径'),
    'stats_dir': ('路径', '本访视 T1_seg 下的 stats 目录'),
    'segmentation_status': ('文本', '提取快照中 segmentation.json 的 status；缺少状态文件为 missing'),
    'segmentation_anatomical_qc': ('文本', '分割阶段的人工解剖质控记录；not_reviewed=尚未人工审核'),
    'segmentation_stats_extracted': ('0/1', '1=完成状态且分割统计通过解析检查并成功提取'),
    'extraction_note': ('文本', '分割统计未提取原因；空值表示成功提取'),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def slug(text):
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')


def region_zh(name):
    for prefix, hemi, tissue in [('ctx-lh-', '左侧', '皮层'), ('ctx-rh-', '右侧', '皮层')]:
        if name.startswith(prefix):
            return hemi + CORTEX[name[len(prefix):]] + '（' + tissue + '）'
    for prefix, hemi in [('Left-', '左侧'), ('Right-', '右侧')]:
        if name.startswith(prefix):
            return hemi + STRUCTURES[name[len(prefix):]]
    return STRUCTURES[name]


def parse_stats(raw):
    """Use declared column headers, validate finite values and declared row counts."""
    measures, rows, headers, expected, seen = {}, [], None, None, set()
    for line in raw.decode('utf-8').splitlines():
        line = line.strip()
        if line.startswith('# Measure '):
            parts = [x.strip() for x in line[len('# Measure '):].split(',')]
            if len(parts) != 5 or parts[1] in measures:
                raise ValueError('Invalid/duplicate Measure: ' + line)
            float_value = float(parts[3])
            if not math.isfinite(float_value):
                raise ValueError('Non-finite Measure')
            measures[parts[1]] = (parts[3], parts[4], parts[2])
        elif line.startswith('# ColHeaders '):
            headers = line.split()[2:]
        elif line.startswith('# NRows '):
            expected = int(line.split()[-1])
        elif line and not line.startswith('#'):
            values = line.split()
            if headers is None or len(values) != len(headers):
                raise ValueError('Table width/header mismatch')
            row = dict(zip(headers, values))
            if row['StructName'] in seen:
                raise ValueError('Duplicate region')
            seen.add(row['StructName'])
            for key, value in row.items():
                if key != 'StructName' and not math.isfinite(float(value)):
                    raise ValueError('Non-finite table value')
            rows.append(row)
    if not rows or (expected is not None and expected != len(rows)):
        raise ValueError('Missing/truncated table')
    return measures, rows


def features(filename, raw):
    measures, rows = parse_stats(raw)
    values, definitions = {}, {}

    def add(column, value, unit, description, field):
        if column in values:
            raise ValueError('Duplicate column: ' + column)
        values[column] = value
        definitions[column] = {'unit': unit, 'meaning': description,
                               'source': filename, 'field': field}

    if filename != SEG_FILE:
        raise ValueError('Unsupported statistics source: ' + filename)
    for row in rows:
        name = row['StructName']
        add(f'seg__{slug(name)}__volume_mm3', row['Volume_mm3'], 'mm^3',
            region_zh(name) + '体积', f"SegId={row['SegId']}; {name} / Volume_mm3")
    for field, (value, unit, _) in measures.items():
        suffix = '_mm3' if unit == 'mm^3' else ''
        add(f'seg_global__{slug(field)}{suffix}', value, unit,
            GLOBAL[field], '# Measure ' + field)
    for column, value in values.items():
        if float(value) < 0:
            raise ValueError('Negative morphometric value: ' + column)
    return values, definitions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cohort', type=Path, default=BASE / 'recommended_core4_i2_with_i3_T1_rigid.csv')
    parser.add_argument('--seg-root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--output-dir', type=Path, default=BASE)
    args = parser.parse_args()
    started = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
    cohort_bytes = args.cohort.read_bytes()
    cohort = list(csv.DictReader(io.StringIO(cohort_bytes.decode('utf-8-sig'))))
    keys = [(r['IID'], r['instance']) for r in cohort]
    assert len(keys) == len(set(keys)), 'Duplicate IID/instance'
    visits = defaultdict(set)
    for iid, instance in keys:
        assert iid.isdigit() and instance in ('2', '3')
        visits[iid].add(instance)
    assert all(v == {'2', '3'} for v in visits.values()), 'Unpaired input IDs'
    assert all(r['sex'] in ('', '0', '1') for r in cohort)
    manifest, schema, snapshots, results, exceptions = [], {}, [], [], []

    def read(path, iid, instance, purpose):
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('Source changed while reading: ' + str(path))
        manifest.append(dict(IID=iid, instance=instance, purpose=purpose, path=str(path),
                             bytes=len(raw), mtime_ns=after.st_mtime_ns, sha256=digest(raw)))
        return raw

    # Freeze status records before reading all statistics from this live processing tree.
    for r in cohort:
        iid, instance = r['IID'], r['instance']
        p = args.seg_root / iid / ('instance_' + instance)
        state = {}
        for stage in ('segmentation',):
            q = p / '_pipeline' / (stage + '.json')
            raw = read(q, iid, instance, 'status_snapshot') if q.exists() else b'{}'
            state[stage] = (json.loads(raw), raw)
        snapshots.append((p, state))

    for index, (r, (p, state)) in enumerate(zip(cohort, snapshots)):
        iid, instance = r['IID'], r['instance']
        seg = state['segmentation'][0]
        out = dict(IID=iid, instance=instance, age=r['age'], sex=r['sex'],
                   cohort_mri_path=r['mri_path'], segmentation_input_path='', stats_dir=str(p / 'stats'),
                   segmentation_status=seg.get('status', 'missing'),
                   segmentation_anatomical_qc=seg.get('anatomical_qc', 'unknown'),
                   segmentation_stats_extracted=0)
        provenance_path = p / '_pipeline/provenance.json'
        if provenance_path.exists():
            provenance = json.loads(read(provenance_path, iid, instance, 'input_provenance'))
            out['segmentation_input_path'] = provenance.get('input_path', '')
        notes = []
        for stage, files in [('segmentation', [SEG_FILE])]:
            if out[stage + '_status'] != 'complete':
                notes.append(stage + '_not_complete')
                continue
            try:
                values, definitions = {}, {}
                for filename in files:
                    raw = read(p / 'stats' / filename, iid, instance, 'statistics')
                    vals, defs = features(filename, raw)
                    assert not values.keys() & vals.keys(), 'Feature collision'
                    values.update(vals)
                    definitions.update(defs)
                current = (p / '_pipeline' / (stage + '.json')).read_bytes()
                assert current == state[stage][1], 'Stage state changed since snapshot'
                for col, definition in definitions.items():
                    if col in schema:
                        assert schema[col] == definition, 'Inconsistent schema: ' + col
                schema.update(definitions)
                out.update(values)
                out[stage + '_stats_extracted'] = 1
            except (OSError, ValueError, KeyError, AssertionError) as error:
                notes.append(stage + '_extraction_error')
                exceptions.append(dict(IID=iid, instance=instance, stage=stage, error=str(error)))
        out['extraction_note'] = ';'.join(notes)
        results.append(out)
        if (index + 1) % 500 == 0:
            print(f'Processed {index + 1}/{len(cohort)} visits', flush=True)

    assert digest(args.cohort.read_bytes()) == digest(cohort_bytes), 'Cohort changed'
    assert [(r['IID'], r['instance']) for r in results] == keys
    columns = list(META) + list(schema)
    assert len(columns) == len(set(columns))
    missing = {c: sum(r.get(c, '') == '' for r in results) for c in columns}
    complete_pairs = {}
    for stage in ('segmentation',):
        counts = Counter(r['IID'] for r in results if r[stage + '_stats_extracted'])
        complete_pairs[stage] = sum(v == 2 for v in counts.values())
    summary = {
        'extraction_started_at': started,
        'extraction_finished_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'cohort_path': str(args.cohort), 'cohort_sha256': digest(cohort_bytes),
        'segmentation_root': str(args.seg_root), 'rows': len(results), 'subjects': len(visits),
        'columns': len(columns), 'metadata_columns': len(META), 'metric_columns': len(schema),
        'visits': dict(Counter(r['instance'] for r in results)),
        'segmentation_status_counts': dict(Counter(r['segmentation_status'] for r in results)),
        'segmentation_extracted_visits': sum(r['segmentation_stats_extracted'] for r in results),
        'complete_pairs': complete_pairs, 'exceptions': exceptions,
        'metrics_by_source': dict(Counter(d['source'] for d in schema.values())),
        'missing_count_by_column': missing,
        'zero_count_by_metric': {c: sum(r.get(c, '') != '' and float(r[c]) == 0 for r in results) for c in schema},
        'source_manifest_rows': len(manifest),
        'limitations': ['existing-statistics extraction only', 'no anatomical QC performed',
                        'no longitudinal pipeline claimed'],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / (STEM + '.csv')
    with csv_path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
    with csv_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == columns
        reread = list(reader)
    assert len(reread) == len(results)
    for original, saved in zip(results, reread):
        assert all(saved[c] == str(original.get(c, '')) for c in columns), 'CSV round-trip mismatch'
    sources_path = args.output_dir / (STEM + '_sources.csv')
    with sources_path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['IID', 'instance', 'purpose', 'path', 'bytes', 'mtime_ns', 'sha256'])
        writer.writeheader()
        writer.writerows(manifest)
    summary['csv_sha256'] = digest(csv_path.read_bytes())
    summary['sources_sha256'] = digest(sources_path.read_bytes())
    summary['script_sha256'] = digest(Path(__file__).read_bytes())
    md = [
        '# UKB84436 双访视脑区指标：数据与列名说明', '',
        f'- 主表：`{csv_path.name}`；UTF-8 BOM 编码，逗号分隔，空单元格表示缺失。',
        f'- 名单：`{args.cohort}`；只按 `(IID, instance)` 匹配，严格保留名单行顺序。',
        f'- 分割根目录：`{args.seg_root}`；只读已有统计，没有重跑或修改影像。',
        f'- 提取开始：{started}；结束：{summary["extraction_finished_at"]}。',
        f'- 共 **{len(visits):,} 人、{len(results):,} 行、{len(columns)} 列**；其中元数据 {len(META)} 列，数值指标 {len(schema)} 列。',
        f'- 分割统计成功提取 {summary["segmentation_extracted_visits"]:,} 次访视；两次访视都成功的受试者 {complete_pairs["segmentation"]:,} 人。',
        f'- 本表仅提取 `{SEG_FILE}`；100 个区域体积加 9 个全脑汇总体积，共 109 个指标。提取异常 {len(exceptions)} 条。', '',
        '## 1. 来源、命名与使用边界', '',
        f'1. 所有数值指标均来自每次访视的 `stats/{SEG_FILE}`。`seg__*` 为区域体积，'
        '`seg_global__*` 为文件头中的全脑汇总体积。保留原始数值及精度，单位均为 mm³。',
        '2. 区域指标包含双侧 DKT 皮层分区、皮层下结构、白质、脑室和胼胝体分区等。'
        '按源文件的 StructName 和 SegId 匹配；体积直接读取 Volume_mm3。',
        '3. 本次提取范围为分割体积。皮层重建统计、厚度、面积、eTIV 和重建处理状态均不纳入。'
        '提取脚本仅读取分割状态、输入溯源和指定统计文件。',
        '4. 0 保留为源统计明确报告的 0；空白表示缺失。源名单的年龄缺失保持为空，不插补。'
        'WM-hypointensities 是 T1 分割标签，不等价于 FLAIR 白质高信号负荷。',
        '5. 所有体积为原始绝对值，未进行颅内容积归一化或年龄/性别校正，未计算访视差值。'
        'MaskVol 是脑掩膜体积，不是 eTIV。',
        '6. 名单中的 rigid MRI 路径用于匹配溯源；实际分割输入见 segmentation_input_path。'
        '工程处理完成不代表人工解剖 QC 通过；原始影像和统计文件保持只读。', '',
        '## 2. 元数据列', '', '| 列名 | 单位/类型 | 含义 | 缺失行数 |', '|---|---|---|---:|',
    ]
    for col, (unit, meaning) in META.items():
        md.append(f'| `{col}` | {unit} | {meaning} | {missing[col]} |')
    md += ['', '## 3. 每个数值列的定义', '',
           '下列顺序与 CSV 数值列一致。脑区中文译名用于阅读，英文原始标签和 SegId 是精确匹配依据。'
           '所有数值指标单位均为 mm³（立方毫米）。', '']
    for filename in [SEG_FILE]:
        md += [f'### 来源：`{filename}`', '', '| 列名 | 中文含义 | 单位 | 源字段/标签 | 缺失行数 |',
               '|---|---|---|---|---:|']
        for col, d in schema.items():
            if d['source'] == filename:
                md.append(f'| `{col}` | {d["meaning"]} | {d["unit"]} | `{d["field"]}` | {missing[col]} |')
        md.append('')
    md += ['## 4. 校验与复现', '',
           f'- 主表 SHA-256：`{summary["csv_sha256"]}`。',
           f'- 源名单 SHA-256：`{summary["cohort_sha256"]}`。',
           f'- `{STEM}_sources.csv`：逐个已读取文件的路径、大小、修改时间和 SHA-256，包含状态快照及实际统计来源。',
           f'- `{STEM}_audit.json`：访视覆盖、配对数、各列缺失/零值计数及提取异常。',
           '- 已验证 ID/访视唯一、每人同时有 i2/i3、行序不变、原名单哈希不变、字段定义一致、数值有限且非负，以及全部 CSV 单元格写入后回读一致。',
           '- 每个文件读取前后检查大小和修改时间；每个完成阶段读取后核对状态快照未改变。'
           '状态树仍在更新，本表是本次快照；若需核对原始文件是否后来变化，可使用来源清单中的 SHA-256。',
           '- 重新提取只读取已有结果，默认覆盖本脚本生成的主表、MD、audit 和 sources 文件；不会启动任何重建进程。'
           '若需保留此次快照，用 `--output-dir` 指定新目录。', '',
           '```bash', f'python {Path(__file__).resolve()}', '```', '',
           '## 5. 官方指标说明', '',
           '- [FastSurfer 输出文件](https://deep-mi.org/FastSurfer/stable/overview/OUTPUT_FILES.html)：分割与表面重建输出文件说明；本表实际来源以本机统计文件头为准。',
           '- [FreeSurfer MorphometryStats](https://freesurfer.net/fswiki/MorphometryStats)：全脑汇总指标的含义（本表无 eTIV）。', '']
    md_path = args.output_dir / (STEM + '.md')
    md_path.write_text('\n'.join(md), encoding='utf-8')
    # Verify the actual delivered dictionary covers every CSV column exactly once.
    delivered_columns = re.findall(r'^\| `([^`]+)` \|', md_path.read_text(), flags=re.M)
    assert Counter(delivered_columns) == Counter(columns), 'MD/CSV column mismatch'
    summary['validation'] = {'csv_roundtrip_all_cells': True, 'dictionary_covers_all_columns': True,
                             'cohort_unchanged': True, 'row_order_preserved': True}
    (args.output_dir / (STEM + '_audit.json')).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in
                      ('missing_count_by_column', 'zero_count_by_metric')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

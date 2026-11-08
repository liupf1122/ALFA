"""Create frozen person-level train/val/test manifests; never overwrite splits."""
from pathlib import Path
import pandas as pd
import numpy as np
from .dataset import audit_splits
from .utils.runtime import sha256, write_json


def partition_subjects(ids, data, seed):
    """Ratios are fractions of all subjects; round val/test, give train the remainder."""
    ids = np.array(sorted(set(ids)), dtype=object)
    np.random.RandomState(seed).shuffle(ids)
    n_val = int(round(len(ids) * data['val_ratio']))
    n_test = int(round(len(ids) * data['test_ratio']))
    n_train = len(ids) - n_val - n_test
    if min(n_train, n_val, n_test) <= 0:
        raise ValueError('Too few subjects to create three nonempty splits')
    return {'train': ids[:n_train].tolist(),
            'val': ids[n_train:n_train+n_val].tolist(),
            'test': ids[n_train+n_val:].tolist()}


def prepare(cfg, headers=False):
    out = Path(cfg['data']['split_dir'])
    files = [out / f'{s}.csv' for s in ['train', 'val', 'test']]
    if all(p.exists() for p in files):
        return audit_splits(cfg, headers=headers)[0]
    if any(p.exists() for p in files):
        raise FileExistsError(f'Incomplete existing split directory: {out}; select a new split_dir')
    d = cfg['data']
    raw = pd.read_csv(d['source_csv'], dtype={'IID': str, 'id': str, 'eid': str})
    if 'IID' in raw:
        required = ['IID', 'instance', 'mri_path', *d['conditions']]
        if set(required) - set(raw.columns): raise ValueError(f'Required source columns: {required}')
        if raw[['IID', 'instance', 'mri_path']].isna().any().any():
            raise ValueError('Missing IID, instance or mri_path')
        visits = pd.to_numeric(raw.instance, errors='raise')
        if not visits.isin([2, 3]).all(): raise ValueError('Expected instance 2 or 3')
        raw['instance'] = visits.astype(int)
        raw['eid'] = raw.IID
        raw['id'] = raw.IID + '_20252_' + raw.instance.astype(str) + '_0'
        raw['image_path'] = raw.mri_path
    raw = raw[['id', 'eid', 'image_path', *d['conditions']]].copy()
    missing = [p for p in raw.image_path if not Path(p).is_file()]
    if missing:
        raise FileNotFoundError(f'{len(missing)} images missing; first: {missing[0]}')
    if raw.id.duplicated().any():
        raise ValueError('Duplicate scan IDs in source table')
    if not all(k in d for k in ['train_ratio', 'val_ratio', 'test_ratio']):
        raise ValueError('Legacy split configuration requires existing split snapshots')
    groups = partition_subjects(raw.eid.unique(), d, cfg['seed'])
    tables = {s: raw.loc[raw.eid.isin(ids)] for s, ids in groups.items()}
    if any(t.empty for t in tables.values()):
        raise ValueError('Too few subjects to create three nonempty splits')
    out.mkdir(parents=True, exist_ok=True)
    for s, table in tables.items():
        table.to_csv(out / f'{s}.csv', index=False)
    audit, _ = audit_splits(cfg, headers=headers)
    write_json(out / 'manifest.json', {**audit, 'source_csv': d['source_csv'],
        'source_sha256': sha256(d['source_csv']), 'seed': cfg['seed'],
        'missing_conditions': raw[d['conditions']].isna().sum().to_dict(),
        'split_policy': 'person-level random split; ratios relative to all subjects; '
                        'round val/test subject counts, train receives the remainder',
        'split_ratios': {s: d[f'{s}_ratio'] for s in ['train', 'val', 'test']}})
    return audit

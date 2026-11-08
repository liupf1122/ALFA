"""Cache-first MRI access, fixed subject splits and training-only normalization."""
from pathlib import Path
import numpy as np
import pandas as pd
import SimpleITK as sitk
import torch
from torch.utils.data import Dataset
from .config import validate_normalization
from .utils.runtime import sha256
from .volume_cache import load_p999


class ConditionNormalizer:
    def __init__(self, names, params):
        self.names, self.params = list(names), params

    @classmethod
    def fit(cls, table, names):
        params = {}
        for name in names:
            values = pd.to_numeric(table[name], errors='coerce').replace([np.inf, -np.inf], np.nan).dropna()
            lo, hi = (float(values.min()), float(values.max())) if len(values) else (0., 1.)
            params[name] = {'min': lo, 'max': hi if hi > lo else lo + 1.}
        return cls(names, params)

    def normalize(self, name, value):
        if pd.isna(value) or not np.isfinite(float(value)):
            return 0.
        p = self.params[name]
        return 2. * (float(value) - p['min']) / (p['max'] - p['min']) - 1.

    def vector(self, row):
        return torch.tensor([self.normalize(n, row[n]) for n in self.names], dtype=torch.float32)

    def state_dict(self):
        return {'names': self.names, 'params': self.params}

    @classmethod
    def from_state(cls, state):
        return cls(state['names'], state['params'])


def read_table(path, cfg):
    table = pd.read_csv(path, dtype={'id': str, 'eid': str})
    required = ['id', 'eid', 'image_path', *cfg['data']['conditions']]
    missing = set(required) - set(table.columns)
    if missing or table.empty:
        raise ValueError(f'Invalid/empty manifest {path}: missing {sorted(missing)}')
    if table[['id', 'eid', 'image_path']].isna().any().any() or table.id.duplicated().any():
        raise ValueError(f'Missing identifiers or duplicate scans in {path}')
    for n in cfg['data']['conditions']:
        table[n] = pd.to_numeric(table[n], errors='raise')
    return table


def audit_splits(cfg, headers=False):
    tables, hashes, sets, counts, geometry = {}, {}, {}, {}, None
    for split in ['train', 'val', 'test']:
        p = Path(cfg['data']['split_dir']) / f'{split}.csv'
        t = read_table(p, cfg)
        tables[split], hashes[split], sets[split] = t, sha256(p), set(t.eid)
        counts[split] = {'scans': len(t), 'subjects': t.eid.nunique()}
        for row in t.itertuples():
            path = Path(row.image_path)
            if not path.is_absolute() or not path.is_file():
                raise FileNotFoundError(f'Image unavailable: {path}')
            if headers:
                r = sitk.ImageFileReader(); r.SetFileName(str(path)); r.ReadImageInformation()
                g = [*r.GetSize(), *r.GetSpacing(), *r.GetOrigin(), *r.GetDirection()]
                if r.GetDimension() != 3:
                    raise ValueError(f'Expected 3D image: {path}')
                if geometry is None:
                    geometry = g
                elif not np.allclose(g, geometry, atol=1e-4, rtol=0):
                    raise ValueError(f'Geometry differs from reference: {path}')
    for a, b in [('train', 'val'), ('train', 'test'), ('val', 'test')]:
        if sets[a] & sets[b]:
            raise ValueError(f'Subject leakage between {a} and {b}')
        if set(tables[a].image_path.map(lambda p: str(Path(p).resolve()))) & set(tables[b].image_path.map(lambda p: str(Path(p).resolve()))):
            raise ValueError(f'Image path overlap between {a} and {b}')
    return {'counts': counts, 'split_sha256': hashes, 'geometry_checked': headers}, tables


def read_volume(row, cfg):
    """Use adjacent p999 caches, converting x,y,z to model z,y,x exactly once."""
    validate_normalization(cfg)
    array, _ = load_p999(row['image_path'])
    return torch.from_numpy(np.array(array.transpose(2, 1, 0), dtype=np.float32, order='C'))


class MRIDataset(Dataset):
    def __init__(self, table, cfg, normalizer):
        self.table = table.reset_index(drop=True)
        self.cfg, self.normalizer = cfg, normalizer
        self.latent_keys = list(dict.fromkeys(self.table.eid))
        self.key_index = {key: i for i, key in enumerate(self.latent_keys)}

    def __len__(self):
        return len(self.table)

    def __getitem__(self, index):
        row = self.table.iloc[index]
        return {'id': row.id, 'eid': row.eid, 'local_id': self.key_index[row.eid],
                't1': read_volume(row, self.cfg), 'conditions': self.normalizer.vector(row)}

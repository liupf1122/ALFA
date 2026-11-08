"""MRI-adjacent ALFA p99.9 caches: reuse first, create lazily under a file lock."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import tempfile
import nibabel as nib
import numpy as np
from .utils.runtime import sha256

NORMALIZATION = 'clip(raw / percentile(raw[raw>0],99.9),0,1)'


def cache_paths(path):
    path = Path(path)
    return {key: Path(str(path) + suffix) for key, suffix in {
        'array': '.alfa-p999.npy', 'meta': '.alfa-p999.json',
        'foreground': '.alfa-p999-foreground.npy', 'lock': '.alfa-p999.lock'}.items()}


def _existing(path):
    paths = cache_paths(path)
    try:
        meta = json.loads(paths['meta'].read_text())
        stat = path.stat()
        if (Path(meta['mri_path']).resolve() != path.resolve() or
                meta['source_bytes'] != stat.st_size or meta['source_mtime_ns'] != stat.st_mtime_ns or
                meta['normalization'] != NORMALIZATION or meta.get('axis_order', 'xyz') != 'xyz' or
                not np.isfinite(meta['scale']) or meta['scale'] <= 0):
            return None
        array = np.load(paths['array'], mmap_mode='r', allow_pickle=False)
        if (array.dtype != np.float32 or array.ndim != 3 or min(array.shape) < 2 or
                list(array.shape) != meta['shape'] or not np.isfinite(array).all() or
                array.min() < 0 or array.max() > 1):
            return None
        # Historical cache_path/foreground_path point to a moved directory: ignore them.
        return array, meta
    except (OSError, ValueError, KeyError, TypeError, EOFError):
        return None


@contextmanager
def _lock(path):
    with path.open('a') as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _atomic(path, writer):
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.', suffix='.tmp', delete=False) as f:
            temp = Path(f.name)
            writer(f)
            f.flush(); os.fsync(f.fileno())
        temp.replace(path)
    finally:
        if temp is not None and temp.exists(): temp.unlink()


def load_p999(path):
    """Return x,y,z float32 cache and metadata. Never mutate the source NIfTI."""
    path = Path(path)
    if not path.is_file(): raise FileNotFoundError(path)
    cached = _existing(path)
    if cached is not None: return cached
    paths = cache_paths(path)
    with _lock(paths['lock']):
        cached = _existing(path)
        if cached is not None: return cached
        before = path.stat()
        image = nib.load(path)
        raw = image.get_fdata(dtype=np.float32)
        if raw.ndim != 3 or min(raw.shape) < 2 or not np.isfinite(raw).all():
            raise ValueError(f'Invalid 3D MRI: {path}')
        positive = raw[raw > 0]
        if not len(positive): raise ValueError(f'No positive MRI intensities: {path}')
        scale = float(np.percentile(positive.astype(np.float64), 99.9))
        volume = np.clip(raw / scale, 0, 1).astype(np.float32)
        foreground = np.flatnonzero(volume.reshape(-1) > .05)
        foreground = foreground.astype(np.int32 if volume.size <= np.iinfo(np.int32).max else np.int64)
        source_hash = sha256(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f'MRI changed during cache construction: {path}')
        meta = {'mri_path': str(path.resolve()), 'cache_path': str(paths['array']),
            'foreground_path': str(paths['foreground']), 'source_bytes': after.st_size,
            'source_mtime_ns': after.st_mtime_ns, 'source_sha256': source_hash,
            'shape': list(volume.shape), 'axis_order': 'xyz', 'dtype': 'float32',
            'affine': image.affine.tolist(), 'zooms': [float(v) for v in image.header.get_zooms()],
            'qform_code': int(image.header['qform_code']), 'sform_code': int(image.header['sform_code']),
            'units': list(image.header.get_xyzt_units()), 'scale': scale,
            'min': float(raw.min()), 'max': float(raw.max()),
            'negative_voxels': int((raw < 0).sum()), 'clipped_high_voxels': int((raw > scale).sum()),
            'foreground_voxels': len(foreground), 'voxel_count': volume.size,
            'normalization': NORMALIZATION,
            'foreground_definition': 'normalized intensity > 0.05; not an anatomical brain mask'}
        # Metadata is the commit marker: publish it only after both arrays are complete.
        _atomic(paths['array'], lambda f: np.save(f, volume, allow_pickle=False))
        _atomic(paths['foreground'], lambda f: np.save(f, foreground, allow_pickle=False))
        meta['cache_sha256'] = sha256(paths['array'])
        _atomic(paths['meta'], lambda f: f.write(json.dumps(meta, indent=2, allow_nan=False).encode()))
        return np.load(paths['array'], mmap_mode='r', allow_pickle=False), meta

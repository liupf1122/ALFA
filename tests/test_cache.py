"""Cache priority, axis convention, regeneration and export scale contracts."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import nibabel as nib
import numpy as np
import pandas as pd
from src.config import load_config
from src.dataset import read_volume
from src.inference import export_volume
from src.prepare import prepare
from src.utils.runtime import sha256
from src.volume_cache import cache_paths, load_p999


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.path = self.root / 'test.nii.gz'
        self.raw = np.arange(4*5*6, dtype=np.float32).reshape(4, 5, 6) - 4
        image = nib.Nifti1Image(self.raw, np.diag([1.2, 1.3, 1.4, 1.]))
        image.set_qform(image.affine, 1); image.set_sform(image.affine, 2)
        nib.save(image, self.path)
        self.cfg = load_config()
        self.row = {'image_path': str(self.path), 'id': 'a'}

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_cache_create_and_priority(self):
        source_hash = sha256(self.path)
        array, meta = load_p999(self.path)
        expected = np.clip(self.raw / np.percentile(self.raw[self.raw > 0].astype(np.float64), 99.9), 0, 1)
        np.testing.assert_allclose(array, expected, atol=1e-7)
        paths = cache_paths(self.path)
        stamps = {k: paths[k].stat().st_mtime_ns for k in ['array', 'meta', 'foreground']}
        # A valid cache must not read/decompress the source NIfTI.
        with patch('src.volume_cache.nib.load', side_effect=AssertionError('source read on cache hit')):
            actual = read_volume(self.row, self.cfg).numpy()
        np.testing.assert_allclose(actual, expected.transpose(2, 1, 0), atol=1e-7)
        self.assertEqual(stamps, {k: paths[k].stat().st_mtime_ns for k in stamps})
        self.assertEqual(source_hash, sha256(self.path))

    def test_invalid_cache_rebuilt(self):
        _, first = load_p999(self.path)
        p = cache_paths(self.path)
        p['array'].write_bytes(b'invalid npy')
        array, meta = load_p999(self.path)
        self.assertEqual(array.shape, self.raw.shape)
        self.assertEqual(meta['scale'], first['scale'])
        self.assertEqual(meta['cache_sha256'], sha256(p['array']))

    def test_historical_metadata_paths_are_ignored(self):
        load_p999(self.path)
        p = cache_paths(self.path)
        meta = json.loads(p['meta'].read_text())
        meta['cache_path'] = '/removed/old/cache.npy'; meta.pop('axis_order')
        p['meta'].write_text(json.dumps(meta))
        with patch('src.volume_cache.nib.load', side_effect=AssertionError('unnecessary rebuild')):
            a, _ = load_p999(self.path)
        self.assertEqual(a.shape, self.raw.shape)

    def test_export_uses_per_scan_scale(self):
        array, meta = load_p999(self.path)
        out = self.root / 'out.nii.gz'
        export_volume(np.array(array.transpose(2, 1, 0)), self.path, out, self.cfg)
        restored = nib.load(out)
        np.testing.assert_allclose(restored.get_fdata(), np.clip(self.raw, 0, meta['scale']), atol=1e-5)
        self.assertEqual(int(restored.header['sform_code']), 2)

    def test_each_scan_uses_its_own_percentile(self):
        path = self.root / 'seven_times_brighter.nii.gz'
        nib.save(nib.Nifti1Image(self.raw * 7, np.eye(4)), path)
        first, first_meta = load_p999(self.path)
        second, second_meta = load_p999(path)
        np.testing.assert_allclose(first, second, atol=1e-7)
        self.assertAlmostEqual(second_meta['scale'] / first_meta['scale'], 7.)
        np.testing.assert_allclose(read_volume({'image_path': str(path)}, self.cfg).numpy(),
                                   first.transpose(2, 1, 0), atol=1e-7)

    def test_new_source_keeps_pairs_and_missing_age(self):
        rows = []
        for i in range(12):
            for visit in [2, 3]:
                image = self.root / f'{i}_{visit}.nii.gz'
                image.write_bytes(self.path.read_bytes())
                rows.append({'IID': str(i), 'instance': visit, 'mri_path': str(image),
                             'age': np.nan if (i == 0 and visit == 3) else 50+i+visit, 'sex': i % 2})
        source = self.root / 'input.csv'; pd.DataFrame(rows).to_csv(source, index=False)
        self.cfg['data']['source_csv'] = str(source)
        self.cfg['data']['split_dir'] = str(self.root / 'splits')
        prepare(self.cfg)
        tables = [pd.read_csv(self.root/'splits'/f'{s}.csv') for s in ['train', 'val', 'test']]
        all_rows = pd.concat(tables)
        self.assertEqual(len(all_rows), 24)
        self.assertEqual(int(all_rows.age.isna().sum()), 1)
        self.assertTrue(all(all(v == 2 for v in t.eid.value_counts()) for t in tables))


if __name__ == '__main__': unittest.main()

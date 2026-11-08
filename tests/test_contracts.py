"""Scientific/engineering contracts, independent of real MRI availability."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from src.config import load_config, merge, validate
from src.dataset import ConditionNormalizer, MRIDataset, audit_splits
from src.model import build_model, ConditionalSIREN
from src.sampler import coords_from_indices
from src.inference import load_model
from src.prepare import partition_subjects


class Contracts(unittest.TestCase):
    def test_subject_ratios_and_reproducibility(self):
        cfg = load_config()
        for size, expected in [(100, [80, 10, 10]), (1143, [915, 114, 114])]:
            ids = [str(i) for i in range(size)]
            groups = partition_subjects(ids, cfg['data'], cfg['seed'])
            self.assertEqual([len(groups[s]) for s in ['train', 'val', 'test']], expected)
            self.assertEqual(groups, partition_subjects(ids[::-1], cfg['data'], cfg['seed']))
            flattened = sum(groups.values(), [])
            self.assertEqual(len(flattened), len(set(flattened)))
            self.assertEqual(set(flattened), set(ids))

    def test_split_ratios_must_sum_to_one(self):
        cfg = load_config()
        cfg['data']['train_ratio'] = .7
        with self.assertRaisesRegex(ValueError, 'must equal 1'):
            validate(cfg)

    def test_legacy_checkpoint_split_config_still_validates(self):
        cfg = load_config()
        for key in ['train_ratio', 'val_ratio', 'test_ratio']:
            cfg['data'].pop(key)
        cfg['data'].update(single_train_ratio=.9, longitudinal_test_ratio=.5, validation_ratio=.1)
        validate(cfg)

    def test_axis_and_latent_interpolation(self):
        # Known z,y,x ramp must match the sampled grid exactly, including corners.
        latent = torch.arange(24, dtype=torch.float32).reshape(1, 1, 2, 3, 4)
        coords = coords_from_indices(torch.arange(24), (2, 3, 4)).unsqueeze(0)
        values = ConditionalSIREN.sample_latent_at_coords(coords, latent)
        torch.testing.assert_close(values.reshape(-1), latent.reshape(-1))

    def test_default_model_forward_backward(self):
        cfg = load_config()
        model = build_model(cfg)
        coords = torch.zeros(1, 4, 3)
        latent = torch.randn(1, 128, 3, 3, 3, requires_grad=True)
        conditions = torch.ones(1, 4, len(cfg['data']['conditions']), requires_grad=True)
        out = model(coords, latent, conditions)
        self.assertEqual(out.shape, (1, 4, 1))
        out.sum().backward()
        self.assertTrue(torch.isfinite(latent.grad).all())
        self.assertGreater(float(conditions.grad.abs().sum()), 0)

    def test_normalization_and_identity(self):
        t = pd.DataFrame({'eid': ['a', 'a', 'b'], 'age': [50., 60., np.nan]})
        n = ConditionNormalizer.fit(t, ['age'])
        self.assertEqual(n.normalize('age', 50), -1)
        self.assertEqual(n.normalize('age', 60), 1)
        self.assertEqual(n.normalize('age', np.nan), 0)
        self.assertEqual(n.normalize('age', 70), 3)  # no silent clipping of extrapolation
        ds = MRIDataset(t, load_config(), n)
        self.assertEqual(ds.latent_keys, ['a', 'b'])
        self.assertEqual(ds.key_index['a'], 0)

    def test_split_leakage_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory); image = p / 'placeholder.nii'; image.touch()
            cfg = merge(load_config(), {'data': {'split_dir': directory, 'conditions': []}})
            for s in ['train', 'val', 'test']:
                pd.DataFrame([{'id': s, 'eid': 'same_person', 'image_path': str(image)}]).to_csv(p/f'{s}.csv', index=False)
            with self.assertRaisesRegex(ValueError, 'Subject leakage'):
                audit_splits(cfg)

    def test_unknown_configuration_key(self):
        with self.assertRaises(ValueError):
            merge(load_config(), {'train': {'epohcs': 2}})

    def test_fixed_scale_configuration_rejected(self):
        cfg = load_config()
        cfg['data']['normalization'] = 'linear'
        with self.assertRaisesRegex(ValueError, 'per-scan p99.9'):
            validate(cfg)
        with self.assertRaisesRegex(ValueError, 'Unknown configuration key'):
            merge(load_config(), {'data': {'norm_scale': 1500.}})

    def test_fixed_scale_checkpoint_rejected_before_model_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'old.pt'
            cfg = load_config()
            cfg['data'].pop('normalization')
            torch.save({'format_version': 1, 'config': cfg}, path)
            with self.assertRaisesRegex(ValueError, 'fixed-scale checkpoints are incompatible'):
                load_model(path, torch.device('cpu'))


if __name__ == '__main__':
    unittest.main()

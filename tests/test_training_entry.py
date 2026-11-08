"""One-command preparation and GPU selection without launching training."""
import os
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd
import torch
from src.config import ROOT, load_config
from src.train import backward_step, train
from src.utils.runtime import select_device, sha256


class GPUSelectionTests(unittest.TestCase):
    def test_most_free_visible_gpu_and_visibility_preserved(self):
        with patch.dict(os.environ, {'CUDA_VISIBLE_DEVICES': '4,2,6'}), \
             patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.device_count', return_value=3), \
             patch('torch.cuda.mem_get_info', side_effect=[(4, 24), (12, 24), (9, 24)]) as query, \
             patch('torch.cuda.set_device') as set_device, \
             patch('torch.cuda.get_device_name', return_value='test GPU'):
            device = select_device('auto', require_cuda=True)
            self.assertEqual(str(device), 'cuda:1')
            self.assertEqual([call.args[0] for call in query.call_args_list], [0, 1, 2])
            self.assertEqual(os.environ['CUDA_VISIBLE_DEVICES'], '4,2,6')
            set_device.assert_called_once_with(device)

    def test_unqueryable_gpu_is_skipped(self):
        with patch('torch.cuda.is_available', return_value=True), \
             patch('torch.cuda.device_count', return_value=2), \
             patch('torch.cuda.mem_get_info', side_effect=[RuntimeError('unavailable'), (12, 24)]), \
             patch('torch.cuda.set_device'), patch('torch.cuda.get_device_name', return_value='test GPU'):
            self.assertEqual(str(select_device('auto', require_cuda=True)), 'cuda:1')

    def test_no_gpu_does_not_silently_train_on_cpu(self):
        with patch('torch.cuda.is_available', return_value=False):
            with self.assertRaisesRegex(RuntimeError, '--device cpu'):
                select_device('auto', require_cuda=True)
            self.assertEqual(str(select_device('cpu', require_cuda=True)), 'cpu')


class TrainingEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cfg = load_config()
        self.cfg['data']['source_csv'] = str(self.root / 'source.csv')
        self.cfg['data']['split_dir'] = str(self.root / 'splits')
        self.cfg['output_dir'] = str(self.root / 'runs')
        rows = []
        for iid in range(12):
            for visit in [2, 3]:
                path = self.root / f'{iid}_{visit}.nii.gz'
                # Preflight checks paths, not voxel contents; decoding must never occur here.
                path.touch()
                rows.append({'IID': str(iid), 'instance': visit, 'mri_path': str(path),
                             'age': 50 + iid + visit, 'sex': iid % 2})
        pd.DataFrame(rows).to_csv(self.cfg['data']['source_csv'], index=False)

    def tearDown(self):
        self.tmp.cleanup()

    def test_prepare_once_and_check_only_never_constructs_model(self):
        with patch('src.train.build_model', side_effect=AssertionError('check-only constructed model')):
            result = train(self.cfg, device='cpu', check_only=True)
            hashes = result['split_sha256']
            self.assertEqual(result['status'], 'ready')
            self.assertFalse(result['training_started'])
            self.assertEqual(sum(c['scans'] for c in result['counts'].values()), 24)
            with patch('src.train.prepare', side_effect=AssertionError('existing splits recreated')):
                again = train(self.cfg, device='cpu', check_only=True)
            self.assertEqual(hashes, again['split_sha256'])
        self.assertFalse(Path(self.cfg['output_dir']).exists())

    def test_partial_split_is_not_overwritten(self):
        split = Path(self.cfg['data']['split_dir']); split.mkdir()
        path = split / 'train.csv'; path.write_text('existing content\n')
        before = sha256(path)
        with self.assertRaisesRegex(FileExistsError, 'Incomplete existing split'):
            train(self.cfg, device='cpu', check_only=True)
        self.assertEqual(sha256(path), before)

    def test_resume_does_not_recreate_missing_splits(self):
        checkpoint = self.root / 'last.pt'
        torch.save({'format_version': 1, 'epoch': 1, 'config': self.cfg}, checkpoint)
        with patch('src.train.prepare', side_effect=AssertionError('resume repartitioned data')):
            with self.assertRaises(FileNotFoundError):
                train(resume=checkpoint, device='cpu', check_only=True)
        self.assertFalse(Path(self.cfg['data']['split_dir']).exists())

    def small_training_config(self):
        cfg = load_config(ROOT / 'experiments/smoke/config.yaml')
        cfg['data'] = self.cfg['data']
        cfg['output_dir'] = self.cfg['output_dir']
        cfg['train']['epochs'] = 1
        return cfg

    def test_persistent_overflow_stops_and_records_failure(self):
        with patch('src.dataset.read_volume', return_value=torch.ones(2, 2, 2)), \
             patch('src.train.backward_step', return_value=False) as step, \
             patch('src.train.MAX_CONSECUTIVE_AMP_OVERFLOWS', 2):
            with self.assertRaisesRegex(FloatingPointError, '2 consecutive AMP'):
                train(self.small_training_config(), device='cpu')
        self.assertEqual(step.call_count, 2)
        run = next(Path(self.cfg['output_dir']).iterdir())
        self.assertEqual(json.loads((run / 'run_info.json').read_text())['status'], 'failed')
        self.assertEqual(len((run / 'logs/amp_overflows.jsonl').read_text().splitlines()), 2)
        self.assertFalse((run / 'checkpoints/last.pt').exists())

    def test_epoch_with_no_updates_does_not_validate_or_checkpoint(self):
        with patch('src.dataset.read_volume', return_value=torch.ones(2, 2, 2)), \
             patch('src.train.backward_step', return_value=False), \
             patch('src.train.validation_score') as validation:
            with self.assertRaisesRegex(FloatingPointError, 'No successful optimizer updates'):
                train(self.small_training_config(), device='cpu')
        validation.assert_not_called()
        run = next(Path(self.cfg['output_dir']).iterdir())
        self.assertFalse((run / 'checkpoints/last.pt').exists())

    def test_skip_accounting_and_checkpoint_after_recovery(self):
        calls = 0
        def skip_once(*args):
            nonlocal calls
            calls += 1
            return False if calls == 1 else backward_step(*args)
        with patch('src.dataset.read_volume', return_value=torch.ones(2, 2, 2)), \
             patch('src.train.backward_step', side_effect=skip_once), \
             patch('src.train.validation_score', return_value=(.1, [])):
            result = train(self.small_training_config(), device='cpu')
        metrics = json.loads((Path(result['run_dir']) / 'logs/metrics.jsonl').read_text())
        self.assertEqual(metrics['amp_skipped_steps'], 1)
        self.assertEqual(metrics['optimizer_steps'], calls - 1)
        checkpoint = torch.load(result['checkpoint_last'], weights_only=False)
        self.assertEqual(checkpoint['consecutive_amp_overflows'], 0)
        self.assertEqual(checkpoint['train_mae'], metrics['train_mae'])


if __name__ == '__main__':
    unittest.main()

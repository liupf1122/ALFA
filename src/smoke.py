"""Bounded synthetic CPU validation; deliberately not a scientific experiment."""
from pathlib import Path
from unittest.mock import patch
import numpy as np
import nibabel as nib
import pandas as pd
import SimpleITK as sitk
import torch
from .config import ROOT, load_config, merge, save_config
from .evaluator import evaluate
from .inference import infer, load_model, fit_latent, predict_volume
from .dataset import MRIDataset, read_volume
from .prepare import prepare
from .train import train
from .utils.runtime import new_run, update_run, write_json


def smoke():
    torch.set_num_threads(1)
    cfg = load_config(ROOT / 'experiments/smoke/config.yaml')
    suite = new_run(cfg, 'smoke_suite')
    update_run(suite, status='running', purpose='synthetic CPU engineering verification only')
    try:
        images = suite / 'synthetic_images'; images.mkdir()
        cfg['output_dir'] = str(suite / 'runs')
        cfg['data']['source_csv'] = str(suite / 'synthetic.csv')
        cfg['data']['split_dir'] = str(suite / 'splits')
        rows = []
        z, y, x = np.meshgrid(np.linspace(-1, 1, 8), np.linspace(-1, 1, 9), np.linspace(-1, 1, 10), indexing='ij')
        for subject in range(12):
            for visit in [2, 3]:
                sid = f'{9000000+subject}_20252_{visit}_0'
                volume = np.exp(-((z - subject*.015)**2 + y*y + x*x) * (3 + visit*.1)).astype(np.float32)
                image = sitk.GetImageFromArray(volume)
                image.SetOrigin((12., -4., 7.)); image.SetSpacing((1.2, 1.3, 1.4))
                image.SetDirection((0., -1., 0., 1., 0., 0., 0., 0., 1.))
                path = images / f'{sid}.nii.gz'; sitk.WriteImage(image, str(path))
                ni = nib.load(path)
                ni.set_sform(ni.affine, 2)
                ni.header.set_xyzt_units('mm', 'sec')
                nib.save(ni, path)
                rows.append({'IID': str(9000000+subject), 'instance': visit, 'mri_path': str(path),
                             'age': 50 + subject + (visit-2)*3, 'sex': subject % 2})
        pd.DataFrame(rows).to_csv(cfg['data']['source_csv'], index=False)
        audit = prepare(cfg, headers=True)
        save_config(cfg, suite / 'synthetic_config.yaml')
        full = train(cfg)
        first = train(cfg, epochs=1)
        resumed = train(resume=first['checkpoint_last'], epochs=2, device='cpu')
        a = torch.load(full['checkpoint_last'], map_location='cpu', weights_only=False)
        b = torch.load(resumed['checkpoint_last'], map_location='cpu', weights_only=False)
        for component in ['model', 'latent']:
            assert all(torch.equal(a[component][k], b[component][k]) for k in a[component]), component
        assert a['best_validation_mae'] == b['best_validation_mae']
        assert a['scheduler'] == b['scheduler']
        original_getitem = MRIDataset.__getitem__
        reads = []
        def counted_getitem(dataset, index):
            reads.append(index)
            return original_getitem(dataset, index)
        with patch.object(MRIDataset, '__getitem__', counted_getitem):
            reconstruction = evaluate(full['checkpoint_best'], device='cpu', max_samples=1)
        assert reads == [0], f'Reconstruction loaded a scan more than once: {reads}'
        longitudinal = evaluate(full['checkpoint_best'], device='cpu', max_samples=1, mode='longitudinal')
        table = pd.read_csv(Path(cfg['data']['split_dir']) / 'test.csv', dtype={'id': str, 'eid': str})
        item = table.iloc[0]
        inference = infer(full['checkpoint_best'], item.id, device='cpu', edits={'age': float(item.age)+5})
        ref = sitk.ReadImage(item.image_path)
        for filename in ['reconstruction.nii.gz', 'edited.nii.gz']:
            image = sitk.ReadImage(str(inference / filename))
            assert image.GetSize() == ref.GetSize()
            assert np.allclose(image.GetOrigin(), ref.GetOrigin())
            assert np.allclose(image.GetSpacing(), ref.GetSpacing())
            assert np.allclose(image.GetDirection(), ref.GetDirection())
            assert np.isfinite(sitk.GetArrayFromImage(image)).all()
            ni, ni_ref = nib.load(inference / filename), nib.load(item.image_path)
            np.testing.assert_allclose(ni.affine, ni_ref.affine)
            np.testing.assert_allclose(ni.get_qform(), ni_ref.get_qform())
            np.testing.assert_allclose(ni.get_sform(), ni_ref.get_sform())
            assert ni.header['qform_code'] == ni_ref.header['qform_code']
            assert ni.header['sform_code'] == ni_ref.header['sform_code']
            assert ni.header.get_xyzt_units() == ni_ref.header.get_xyzt_units()
        model, normalizer, checkpoint_cfg, _ = load_model(full['checkpoint_best'], torch.device('cpu'))
        state_before = {k: v.clone() for k, v in model.state_dict().items()}
        volume = read_volume(item, cfg)
        c = normalizer.vector(item)
        latent = fit_latent(model, volume, c, checkpoint_cfg, torch.device('cpu'))
        assert all(torch.equal(v, model.state_dict()[k]) for k, v in state_before.items())
        p1 = predict_volume(model, latent, volume.shape, c, 256, torch.device('cpu'))
        p2 = predict_volume(model, latent, volume.shape, c, 127, torch.device('cpu'))
        np.testing.assert_allclose(p1, p2, atol=1e-6, rtol=1e-5)
        ablation_cfg = merge(cfg, {'name': 'smoke_no_conditions', 'data': {'conditions': []}})
        ablation = train(ablation_cfg, epochs=1)
        ablation_eval = evaluate(ablation['checkpoint_best'], device='cpu', max_samples=1)
        result = {'status': 'passed', 'suite_dir': str(suite), 'audit': audit,
            'checks': ['five-column IID/instance source preparation', 'lazy adjacent p999 cache creation', 'subject-disjoint splits', 'training + validation + best/last checkpoints',
                'resume matches uninterrupted model and latent bitwise on CPU', 'reconstruction evaluation loads each scan once',
                'i2-only longitudinal evaluation with persistence baseline', 'frozen decoder during latent fit',
                'fixed-latent age edit and NIfTI geometry preservation', 'chunked prediction consistency',
                'NIfTI affine, qform/sform codes and xyzt units retained',
                'no-condition ablation train + evaluate'],
            'baseline_run': full['run_dir'], 'resumed_run': resumed['run_dir'],
            'reconstruction': str(reconstruction), 'longitudinal': str(longitudinal),
            'inference': str(inference), 'ablation_evaluation': str(ablation_eval),
            'scope': 'engineering only; tiny synthetic volumes and reduced network; no real MRI training'}
        write_json(suite / 'verification.json', result)
        update_run(suite, status='completed')
        return result
    except BaseException as exc:
        update_run(suite, status='failed', error=repr(exc)); raise

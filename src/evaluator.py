"""Explicit reconstruction fitting and i2-only longitudinal evaluation protocols."""
from pathlib import Path
import sys
from tqdm import tqdm
import numpy as np
import pandas as pd
import nibabel as nib
from skimage.metrics import structural_similarity
from .dataset import MRIDataset, read_table
from .inference import fit_latent, load_model, predict_volume
from .utils.runtime import new_run, rng_state, restore_rng, select_device, set_seed, sha256, update_run, write_json


def compute_metrics(gt, pred, cfg):
    error = pred.astype(np.float64) - gt
    mse = float(np.mean(error ** 2))
    dr = cfg['inference']['data_range']
    mask = gt > cfg['inference']['foreground_threshold']
    size = min(gt.shape)
    win = min(7, size if size % 2 else size - 1)
    return {'mae': float(np.mean(np.abs(error))), 'mse': mse,
        'psnr': float(10. * np.log10(dr ** 2 / mse)) if mse > 0 else None,
        'ssim': float(structural_similarity(gt, pred, data_range=dr, win_size=win)) if win >= 3 else None,
        'foreground_mae': float(np.mean(np.abs(error[mask]))) if mask.any() else None}


def validation_score(model, dataset, cfg, device):
    # Fixed sample membership, initialization and sampling budget for every validation.
    state = rng_state()
    rows = []
    try:
        set_seed(cfg['seed'] + 10000)
        indices = dataset.table.drop_duplicates('eid').index.tolist()
        limit = cfg['validation']['max_samples']
        if limit is not None: indices = indices[:limit]
        with tqdm(indices, desc='Validation', unit='scan', dynamic_ncols=True,
                  mininterval=1., file=sys.stdout) as progress:
            for index in progress:
                item = dataset[index]
                z = fit_latent(model, item['t1'], item['conditions'], cfg, device, cfg['validation'])
                pred = predict_volume(model, z, item['t1'].shape, item['conditions'], cfg['inference']['chunk_size'], device)
                rows.append({'id': item['id'], **compute_metrics(item['t1'].numpy(), pred, cfg)})
                progress.set_postfix(mae=f'{np.mean([r["mae"] for r in rows]):.6f}', refresh=False)
    finally:
        restore_rng(state)
    if not rows: raise ValueError('Empty validation subset')
    return float(np.mean([r['mae'] for r in rows])), rows


def evaluate(checkpoint_path, device='auto', max_samples=None, mode='reconstruction', manifest=None, fit_steps=None):
    if max_samples is not None and max_samples <= 0: raise ValueError('max_samples must be positive')
    if mode not in ['reconstruction', 'longitudinal']: raise ValueError(f'Unknown mode {mode}')
    dev = select_device(device)
    model, normalizer, cfg, checkpoint = load_model(checkpoint_path, dev)
    cfg['device'] = str(dev)
    if fit_steps is not None:
        if fit_steps <= 0: raise ValueError('fit_steps must be positive')
        cfg['inference']['fit_steps'] = fit_steps
    path = Path(manifest) if manifest else Path(cfg['data']['split_dir']) / 'test.csv'
    if not manifest and sha256(path) != checkpoint['split_sha256']['test']:
        raise ValueError('Test manifest changed since training')
    table = read_table(path, cfg)
    if set(table.eid) & set(checkpoint['latent_keys']):
        raise ValueError('Evaluation manifest includes training subjects')
    dataset = MRIDataset(table, cfg, normalizer)
    pairs, skipped_missing_age = [], []
    if mode == 'longitudinal':
        if 'age' not in normalizer.names: raise ValueError('Longitudinal mode needs age')
        for eid, group in table.groupby('eid', sort=False):
            visits = group.id.str.split('_').str[2]
            i2, i3 = group[visits == '2'], group[visits == '3']
            if len(i2) == len(i3) == 1:
                if not np.isfinite([i2.age.iloc[0], i3.age.iloc[0]]).all():
                    skipped_missing_age.append(str(eid))
                    continue
                pairs.append((int(i2.index[0]), int(i3.index[0])))
    else:
        pairs = [(i, i) for i in range(len(dataset))]
    if max_samples is not None: pairs = pairs[:max_samples]
    if not pairs: raise ValueError('No eligible scans/pairs')
    run = new_run(cfg, 'evaluate_' + mode)
    update_run(run, status='running', checkpoint=str(Path(checkpoint_path).resolve()),
        checkpoint_sha256=sha256(checkpoint_path), manifest_sha256=sha256(path), mode=mode)
    try:
        set_seed(cfg['seed'])
        rows = []
        for src_index, target_index in pairs:
            source = dataset[src_index]
            target = source if target_index == src_index else dataset[target_index]
            z = fit_latent(model, source['t1'], source['conditions'], cfg, dev)
            c = source['conditions'].clone()
            if mode == 'longitudinal':
                if source['t1'].shape != target['t1'].shape: raise ValueError('Paired geometry mismatch')
                source_image = nib.load(table.iloc[src_index].image_path)
                target_image = nib.load(table.iloc[target_index].image_path)
                if not np.allclose(source_image.affine, target_image.affine, atol=1e-4, rtol=0):
                    raise ValueError('Paired physical geometry mismatch')
                # Only age changes; all other conditions and the fitted identity stay fixed.
                age_index = normalizer.names.index('age')
                c[age_index] = target['conditions'][age_index]
            pred = predict_volume(model, z, target['t1'].shape, c, cfg['inference']['chunk_size'], dev)
            row = {'source_id': source['id'], 'target_id': target['id'],
                   **compute_metrics(target['t1'].numpy(), pred, cfg)}
            if mode == 'longitudinal':
                row.update({'persistence_' + k: v for k, v in compute_metrics(target['t1'].numpy(), source['t1'].numpy(), cfg).items()})
                unchanged = predict_volume(model, z, target['t1'].shape, source['conditions'], cfg['inference']['chunk_size'], dev)
                row['unchanged_condition_mae'] = float(np.mean(np.abs(unchanged.astype(np.float64) - target['t1'].numpy())))
                row['delta_mae_vs_persistence'] = row['mae'] - row['persistence_mae']
            rows.append(row)
        pd.DataFrame(rows).to_csv(run / 'metrics.csv', index=False)
        means = pd.DataFrame(rows).select_dtypes(include='number').mean().to_dict()
        means = {k: float(v) if np.isfinite(v) else None for k, v in means.items()}
        write_json(run / 'summary.json', {'mode': mode, 'n': len(rows), 'means': means,
            'skipped_missing_age_subjects': skipped_missing_age,
            'fit_target': 'same scan as scored' if mode == 'reconstruction' else 'i2 only; score against i3',
            'data_range': cfg['inference']['data_range'], 'checkpoint_epoch': checkpoint['epoch']})
        update_run(run, status='completed')
    except BaseException as exc:
        update_run(run, status='failed', error=repr(exc)); raise
    return run

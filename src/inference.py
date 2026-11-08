"""Frozen-decoder latent fitting and fixed-latent condition editing."""
from copy import deepcopy
from pathlib import Path
import numpy as np
import nibabel as nib
import torch
from .config import validate_normalization
from .dataset import ConditionNormalizer, read_table, read_volume
from .loss import reconstruction_loss
from .model import build_model
from .sampler import coords_from_indices, sample_voxels
from .volume_cache import load_p999
from .utils.runtime import new_run, select_device, set_seed, sha256, update_run, write_json


def load_model(checkpoint_path, device):
    # Only load checkpoints produced/trusted by this project.
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    if checkpoint.get('format_version') != 1:
        raise ValueError('Expected ALFA2 v1 checkpoint; legacy checkpoints require explicit conversion')
    cfg = deepcopy(checkpoint['config'])
    validate_normalization(cfg)
    snapshot = Path(checkpoint_path).resolve().parent.parent / 'data/splits'
    if snapshot.is_dir():
        cfg['data']['split_dir'] = str(snapshot)
    model = build_model(cfg).to(device)
    model.load_state_dict(checkpoint['model'])
    model.eval().requires_grad_(False)
    return model, ConditionNormalizer.from_state(checkpoint['normalizer']), cfg, checkpoint


def fit_latent(model, volume, conditions, cfg, device, budget=None):
    settings = budget or cfg['inference']
    volume = volume.to(device).unsqueeze(0)
    conditions = conditions.to(device).view(1, 1, -1)
    z = torch.randn((1, cfg['model']['latent_channels'], *cfg['model']['latent_spatial']), device=device) * .01
    z.requires_grad_(True)
    optimizer = torch.optim.Adam([z], lr=settings['fit_lr'])
    was_training = model.training
    flags = [p.requires_grad for p in model.parameters()]
    model.eval().requires_grad_(False)
    try:
        for _ in range(settings['fit_steps']):
            coords, target = sample_voxels(volume, settings['fit_points'])
            optimizer.zero_grad(set_to_none=True)
            loss = reconstruction_loss(model(coords, z, conditions.expand(1, coords.shape[1], -1)), target)
            if not torch.isfinite(loss):
                raise FloatingPointError('Non-finite latent-fitting loss')
            loss.backward()
            optimizer.step()
    finally:
        for p, flag in zip(model.parameters(), flags):
            p.requires_grad_(flag)
        model.train(was_training)
    return z.detach()


@torch.no_grad()
def predict_volume(model, latent, shape, conditions, chunk_size, device):
    flat = np.empty(int(np.prod(shape)), dtype=np.float32)
    c = conditions.to(device).view(1, 1, -1)
    for start in range(0, len(flat), chunk_size):
        end = min(start + chunk_size, len(flat))
        coords = coords_from_indices(torch.arange(start, end, device=device), shape).unsqueeze(0)
        flat[start:end] = model(coords, latent.to(device), c.expand(1, end-start, -1)).reshape(-1).cpu().numpy()
    if not np.isfinite(flat).all():
        raise FloatingPointError('Non-finite reconstruction')
    return flat.reshape(shape)


def export_volume(array, reference_path, output_path, cfg):
    validate_normalization(cfg)
    reference = nib.load(str(reference_path))
    # SimpleITK arrays are z,y,x; NIfTI data arrays are x,y,z.
    _, meta = load_p999(reference_path)
    raw = (array * meta['scale']).astype(np.float32).transpose(2, 1, 0)
    header = reference.header.copy()
    header.set_data_dtype(np.float32)
    image = reference.__class__(raw, reference.affine, header=header)
    image.set_qform(reference.get_qform(), int(reference.header['qform_code']))
    image.set_sform(reference.get_sform(), int(reference.header['sform_code']))
    image.header.set_xyzt_units(*reference.header.get_xyzt_units())
    image.header.set_slope_inter(1., 0.)
    nib.save(image, str(output_path))


def infer(checkpoint_path, scan_id, device='auto', edits=None, manifest=None, fit_steps=None):
    dev = select_device(device)
    model, normalizer, cfg, checkpoint = load_model(checkpoint_path, dev)
    if fit_steps is not None:
        if fit_steps <= 0: raise ValueError('fit_steps must be positive')
        cfg['inference']['fit_steps'] = fit_steps
    cfg['device'] = str(dev)
    table_path = Path(manifest) if manifest else Path(cfg['data']['split_dir']) / 'test.csv'
    table = read_table(table_path, cfg)
    selected = table.loc[table.id == scan_id]
    if len(selected) != 1:
        raise ValueError(f'Expected exactly one scan for {scan_id}')
    row = selected.iloc[0]
    c = normalizer.vector(row)
    edited = c.clone()
    for key, value in (edits or {}).items():
        if key not in normalizer.names or not np.isfinite(value):
            raise ValueError(f'Invalid condition edit: {key}={value}')
        edited[normalizer.names.index(key)] = normalizer.normalize(key, value)
    run = new_run(cfg, 'inference')
    update_run(run, status='running', checkpoint=str(Path(checkpoint_path).resolve()),
        checkpoint_sha256=sha256(checkpoint_path), manifest_sha256=sha256(table_path), scan_id=scan_id, edits=edits or {})
    try:
        set_seed(cfg['seed'])
        volume = read_volume(row, cfg)
        z = fit_latent(model, volume, c, cfg, dev)
        torch.save({'latent': z.cpu(), 'conditions': c, 'scan_id': scan_id}, run / 'latent.pt')
        pred = predict_volume(model, z, volume.shape, c, cfg['inference']['chunk_size'], dev)
        export_volume(pred, row.image_path, run / 'reconstruction.nii.gz', cfg)
        if edits:
            pred_edit = predict_volume(model, z, volume.shape, edited, cfg['inference']['chunk_size'], dev)
            export_volume(pred_edit, row.image_path, run / 'edited.nii.gz', cfg)
        write_json(run / 'inference.json', {'scan_id': scan_id, 'input_image': row.image_path,
            'fitted_on': scan_id, 'edits': edits or {}, 'latent_fixed_during_edit': True,
            'meaning': 'reconstruction and condition response; not validated future prediction'})
        update_run(run, status='completed')
    except BaseException as exc:
        update_run(run, status='failed', error=repr(exc)); raise
    return run

"""Validated YAML configuration; relative paths are relative to project root."""
from copy import deepcopy
import math
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def merge(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        if key not in result:
            raise ValueError(f"Unknown configuration key: {key}")
        if isinstance(result[key], dict):
            if not isinstance(value, dict):
                raise ValueError(f"Expected mapping for {key}")
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path=None):
    with (ROOT / 'configs/default.yaml').open() as f:
        cfg = yaml.safe_load(f)
    if path:
        with Path(path).open() as f:
            cfg = merge(cfg, yaml.safe_load(f) or {})
    for parent, keys in [(cfg, ['output_dir']), (cfg['data'],
            ['source_csv', 'split_dir'])]:
        for key in keys:
            if parent[key] is not None:
                p = Path(parent[key]).expanduser()
                parent[key] = str((ROOT / p).resolve() if not p.is_absolute() else p)
    validate(cfg)
    return cfg


def validate_normalization(cfg):
    if cfg['data'].get('normalization') != 'p999':
        raise ValueError('Only per-scan p99.9 normalization is supported; fixed-scale checkpoints are incompatible')
    if cfg['data'].get('cache_mode') != 'adjacent':
        raise ValueError('p999 normalization requires adjacent caches')


def validate(cfg):
    validate_normalization(cfg)
    for section, keys in {
        'train': ['epochs', 'batch_size', 'points', 'network_lr', 'latent_lr', 'lr_step', 'lr_gamma', 'grad_clip', 'save_every', 'patience'],
        'validation': ['every', 'fit_steps', 'fit_points', 'fit_lr'],
        'inference': ['fit_steps', 'fit_points', 'fit_lr', 'chunk_size', 'data_range'],
        'model': ['latent_channels', 'backbone_hidden_features', 'backbone_hidden_layers', 'head_hidden_features', 'head_num_layers'],
    }.items():
        for key in keys:
            if cfg[section][key] <= 0:
                raise ValueError(f'{section}.{key} must be positive')
    if cfg['train']['num_workers'] < 0:
        raise ValueError('train.num_workers must be nonnegative')
    if cfg['train']['min_delta'] < 0:
        raise ValueError('train.min_delta must be nonnegative')
    if cfg['validation']['max_samples'] is not None and cfg['validation']['max_samples'] <= 0:
        raise ValueError('validation.max_samples must be positive or null')
    if cfg['model']['head_out_size'] != 1:
        raise ValueError('Only single-channel T1 is supported')
    if len(cfg['model']['latent_spatial']) != 3 or min(cfg['model']['latent_spatial']) <= 0:
        raise ValueError('latent_spatial requires three positive dimensions')
    if len(set(cfg['data']['conditions'])) != len(cfg['data']['conditions']):
        raise ValueError('Duplicate condition names')
    # Legacy checkpoints retain their original split snapshots on resume.
    new_ratios = ['train_ratio', 'val_ratio', 'test_ratio']
    keys = new_ratios if any(k in cfg['data'] for k in new_ratios) else [
        'single_train_ratio', 'longitudinal_test_ratio', 'validation_ratio']
    for key in keys:
        if key not in cfg['data']:
            raise ValueError(f'Missing data.{key}')
        if not 0 < cfg['data'][key] < 1:
            raise ValueError(f'data.{key} must be in (0, 1)')
    if keys == new_ratios and not math.isclose(
            sum(cfg['data'][key] for key in keys), 1., rel_tol=0., abs_tol=1e-9):
        raise ValueError('train_ratio + val_ratio + test_ratio must equal 1')


def save_config(cfg, path):
    Path(path).write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True))

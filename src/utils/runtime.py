"""Run provenance, atomic writes, RNG state and explicit device selection."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import torch
from ..config import ROOT, save_config


def timestamp():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False))
    tmp.replace(path)


def save_checkpoint(path, obj):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp')
    torch.save(obj, tmp)
    tmp.replace(path)


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def rng_state():
    return dict(python=random.getstate(), numpy=np.random.get_state(), torch=torch.get_rng_state(),
                cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [])


def restore_rng(state):
    random.setstate(state['python'])
    np.random.set_state(state['numpy'])
    torch.set_rng_state(state['torch'].cpu())
    if state['cuda'] and torch.cuda.is_available():
        torch.cuda.set_rng_state_all([s.cpu() for s in state['cuda']])


def select_device(value, *, require_cuda=False):
    if value == 'auto':
        if not torch.cuda.is_available():
            if require_cuda:
                raise RuntimeError('No CUDA GPU is visible. For intentional CPU training, use --device cpu')
            print('DEVICE=cpu (CUDA unavailable)', flush=True)
            return torch.device('cpu')
        candidates = []
        visible = os.environ.get('CUDA_VISIBLE_DEVICES', '(all visible devices)')
        print(f'GPU auto-selection: CUDA_VISIBLE_DEVICES={visible}', flush=True)
        for index in range(torch.cuda.device_count()):
            try:
                free, total = torch.cuda.mem_get_info(index)
            except RuntimeError as exc:
                print(f'  skip logical cuda:{index}: {exc}', flush=True)
                continue
            print(f'  logical cuda:{index}: free={free / 2**30:.2f}/{total / 2**30:.2f} GiB', flush=True)
            candidates.append((index, free))
        if not candidates:
            raise RuntimeError('No visible CUDA GPU could be queried; select an available device explicitly')
        selected = max(candidates, key=lambda item: item[1])[0]
        value = f'cuda:{selected}'
    device = torch.device(value)
    if device.type == 'cuda':
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA requested but unavailable')
        torch.cuda.set_device(device)
        print(f'DEVICE={device} ({torch.cuda.get_device_name(device)})', flush=True)
    else:
        print(f'DEVICE={device}', flush=True)
    return device


def new_run(cfg, prefix=None):
    name = prefix or cfg['name']
    if not name or any(c in name for c in '/\\') or name in ['.', '..']:
        raise ValueError('Run name must be a directory basename')
    stamp = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S_%f')
    run = Path(cfg['output_dir']) / f'{name}_seed{cfg["seed"]}_{stamp}'
    run.mkdir(parents=True, exist_ok=False)
    for sub in ['checkpoints', 'logs', 'figures']:
        (run / sub).mkdir()
    save_config(cfg, run / 'config.yaml')
    code = {str(p.relative_to(ROOT)): sha256(p) for folder in ['src', 'scripts', 'analysis']
            for p in sorted((ROOT / folder).rglob('*.py'))}
    versions = {p: importlib.metadata.version(p) for p in
                ['torch', 'numpy', 'pandas', 'SimpleITK', 'nibabel', 'scikit-learn', 'scikit-image', 'PyYAML']}
    write_json(run / 'run_info.json', dict(started=timestamp(), status='created', command=sys.argv,
        python=sys.version, executable=sys.executable, platform=platform.platform(), versions=versions,
        conda_env=os.environ.get('CONDA_DEFAULT_ENV'), cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
        code_sha256=code))
    return run


def update_run(run, **values):
    path = Path(run) / 'run_info.json'
    obj = json.loads(path.read_text())
    obj.update(values)
    write_json(path, obj)

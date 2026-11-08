"""Joint decoder/subject-latent training with validation and complete resume state."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from .config import save_config, validate
from .dataset import ConditionNormalizer, MRIDataset, audit_splits
from .evaluator import validation_score
from .model import LatentManager, build_model
from .loss import reconstruction_loss
from .sampler import sample_voxels
from .prepare import prepare
from .utils.runtime import (new_run, restore_rng, rng_state, save_checkpoint, select_device,
                            set_seed, timestamp, update_run, write_json)


MAX_CONSECUTIVE_AMP_OVERFLOWS = 16


def backward_step(loss, optimizer, scaler, max_norm):
    """Return whether weights updated; AMP overflow must skip clipping and Adam."""
    if not torch.isfinite(loss):
        raise FloatingPointError('Non-finite training loss')
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    parameters = [p for group in optimizer.param_groups for p in group['params']
                  if p.grad is not None]
    if not parameters:
        raise RuntimeError('Training loss produced no parameter gradients')
    finite = torch.stack([torch.isfinite(p.grad).all() for p in parameters]).all()
    if not finite:
        if not scaler.is_enabled():
            raise FloatingPointError('Non-finite training gradients in full precision')
        # unscale_ recorded the overflow. GradScaler skips optimizer.step and reduces
        # the scale; do not clip invalid gradients or modify optimizer state here.
        scaler.step(optimizer)
        scaler.update()
        return False
    # Keep the strict norm check: even finite elements can overflow a norm reduction.
    torch.nn.utils.clip_grad_norm_(parameters, max_norm, error_if_nonfinite=True)
    scaler.step(optimizer)
    scaler.update()
    return True


def train(cfg=None, resume=None, epochs=None, device=None, *, check_only=False):
    saved = None
    if resume:
        saved = torch.load(resume, map_location='cpu', weights_only=False)
        if saved.get('format_version') != 1: raise ValueError('Expected ALFA2 checkpoint')
        cfg = deepcopy(saved['config'])
        # A saved CUDA index is from the previous process; select among today's visible GPUs.
        cfg['device'] = 'auto'
        snapshot = Path(resume).resolve().parent.parent / 'data/splits'
        if snapshot.is_dir(): cfg['data']['split_dir'] = str(snapshot)
    else:
        cfg = deepcopy(cfg)
    if epochs is not None: cfg['train']['epochs'] = epochs
    if device is not None: cfg['device'] = device
    validate(cfg)
    start_epoch = saved['epoch'] if saved else 0
    if cfg['train']['epochs'] <= start_epoch:
        raise ValueError('--epochs is the total epoch limit and must exceed the saved epoch')
    split_files = [Path(cfg['data']['split_dir']) / f'{s}.csv' for s in ['train', 'val', 'test']]
    if saved is None and not all(p.is_file() for p in split_files):
        print('Preparing fixed subject splits...', flush=True)
        prepare(cfg)
    print('Checking fixed splits and MRI paths...', flush=True)
    audit, tables = audit_splits(cfg)
    if saved and saved['split_sha256'] != audit['split_sha256']:
        raise ValueError('Split files changed since checkpoint')
    normalizer = ConditionNormalizer.from_state(saved['normalizer']) if saved else ConditionNormalizer.fit(tables['train'], cfg['data']['conditions'])
    dataset = MRIDataset(tables['train'], cfg, normalizer)
    validation = MRIDataset(tables['val'], cfg, normalizer)
    if saved and saved['latent_keys'] != dataset.latent_keys:
        raise ValueError('Subject-to-latent mapping changed')
    print(f'DATA={json.dumps(audit["counts"], ensure_ascii=False)}', flush=True)
    dev = select_device(cfg['device'], require_cuda=True)
    cfg['device'] = str(dev)
    if check_only:
        return {'status': 'ready', 'training_started': False, 'device': str(dev),
                'split_dir': cfg['data']['split_dir'], 'output_dir': cfg['output_dir'], **audit}
    set_seed(cfg['seed'])
    model = build_model(cfg).to(dev)
    latents = LatentManager(len(dataset.latent_keys),
        (cfg['model']['latent_channels'], *cfg['model']['latent_spatial'])).to(dev)
    optimizer = torch.optim.Adam([{'params': model.parameters(), 'lr': cfg['train']['network_lr']},
                                  {'params': latents.parameters(), 'lr': cfg['train']['latent_lr']}])
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, cfg['train']['lr_step'], cfg['train']['lr_gamma'])
    scaler = torch.amp.GradScaler('cuda', enabled=cfg['train']['mixed_precision'] and dev.type == 'cuda')
    consecutive_overflows = saved.get('consecutive_amp_overflows', 0) if saved else 0
    best, best_epoch, monitor_best, bad_checks = float('inf'), 0, float('inf'), 0
    if saved:
        model.load_state_dict(saved['model']); latents.load_state_dict(saved['latent'])
        optimizer.load_state_dict(saved['optimizer']); scheduler.load_state_dict(saved['scheduler'])
        scaler.load_state_dict(saved['scaler'])
        best, best_epoch = saved['best_validation_mae'], saved['best_epoch']
        monitor_best, bad_checks = saved['monitor_best'], saved['bad_checks']
        restore_rng(saved['rng'])
    loader = DataLoader(dataset, batch_size=cfg['train']['batch_size'], shuffle=True,
        num_workers=cfg['train']['num_workers'], pin_memory=dev.type == 'cuda',
        persistent_workers=cfg['train']['num_workers'] > 0)
    run = new_run(cfg)
    print(f'RUN_DIR={run}', flush=True)
    snapshot = run / 'data/splits'; snapshot.mkdir(parents=True)
    for split in ['train', 'val', 'test']:
        shutil.copy2(Path(cfg['data']['split_dir']) / f'{split}.csv', snapshot / f'{split}.csv')
    cfg['data']['split_dir'] = str(snapshot)
    save_config(cfg, run / 'config.yaml')
    update_run(run, status='running', device=str(dev), **audit,
        resume_from=str(Path(resume).resolve()) if resume else None,
        selection_metric='validation reconstruction MAE after fixed-budget latent fitting',
        validation_ids=validation.table.drop_duplicates('eid').id.tolist()[:cfg['validation']['max_samples']])
    try:
        if saved and best_epoch:
            source_best = Path(resume).resolve().parent / 'best.pt'
            prior = torch.load(source_best, map_location='cpu', weights_only=False)
            if prior['epoch'] != best_epoch or prior['best_validation_mae'] != best:
                raise ValueError('Matching best.pt is required to resume this checkpoint')
            shutil.copy2(source_best, run / 'checkpoints/best.pt')
        stop_reason = 'epoch_limit'
        for epoch in range(start_epoch + 1, cfg['train']['epochs'] + 1):
            model.train()
            total, count = 0., 0
            skipped_steps, optimizer_steps = 0, 0
            with tqdm(loader, desc=f'Train {epoch}/{cfg["train"]["epochs"]}',
                      unit='batch', dynamic_ncols=True, mininterval=1., file=sys.stdout) as progress:
                for batch_index, batch in enumerate(progress, start=1):
                    volume = batch['t1'].to(dev, non_blocking=True)
                    c = batch['conditions'].to(dev)
                    z = latents(batch['local_id'].to(dev))
                    coords, target = sample_voxels(volume, cfg['train']['points'])
                    optimizer.zero_grad(set_to_none=True)
                    with torch.amp.autocast(dev.type, enabled=scaler.is_enabled()):
                        pred = model(coords, z, c.unsqueeze(1).expand(-1, coords.shape[1], -1))
                        loss = reconstruction_loss(pred, target)
                    previous_scale = scaler.get_scale()
                    updated = backward_step(loss, optimizer, scaler, cfg['train']['grad_clip'])
                    if not updated:
                        skipped_steps += 1
                        consecutive_overflows += 1
                        event = {'epoch': epoch, 'batch': batch_index, 'event': 'amp_overflow',
                                 'previous_scale': previous_scale, 'loss_scale': scaler.get_scale(),
                                 'consecutive_overflows': consecutive_overflows}
                        with (run / 'logs/amp_overflows.jsonl').open('a') as f:
                            f.write(json.dumps(event, allow_nan=False) + '\n')
                        tqdm.write(f'AMP overflow: epoch={epoch} batch={batch_index}; update skipped, '
                                   f'scale={previous_scale:g}->{scaler.get_scale():g}', file=sys.stdout)
                        progress.set_postfix(mae=f'{total/count:.6f}' if count else 'n/a',
                                             amp_skips=skipped_steps, refresh=False)
                        if consecutive_overflows >= MAX_CONSECUTIVE_AMP_OVERFLOWS:
                            raise FloatingPointError(
                                f'{consecutive_overflows} consecutive AMP gradient overflows; '
                                'check data/model stability or set train.mixed_precision: false')
                        continue
                    consecutive_overflows = 0
                    optimizer_steps += 1
                    total += float(loss.detach()) * len(volume); count += len(volume)
                    progress.set_postfix(mae=f'{total/count:.6f}', amp_skips=skipped_steps, refresh=False)
            if count == 0:
                raise FloatingPointError('No successful optimizer updates in this epoch; '
                                         'all batches overflowed in AMP')
            scheduler.step()
            value, is_best, validation_rows = None, False, []
            if epoch % cfg['validation']['every'] == 0 or epoch == cfg['train']['epochs']:
                value, validation_rows = validation_score(model, validation, cfg, dev)
                if value < best:
                    best, best_epoch, is_best = value, epoch, True
                if value < monitor_best - cfg['train']['min_delta']:
                    monitor_best, bad_checks = value, 0
                else:
                    bad_checks += 1
            record = {'epoch': epoch, 'train_mae': total / count, 'validation_mae': value,
                      'optimizer_steps': optimizer_steps, 'amp_skipped_steps': skipped_steps,
                      'loss_scale': scaler.get_scale(),
                      'network_lr': optimizer.param_groups[0]['lr'], 'bad_validation_checks': bad_checks}
            with (run / 'logs/metrics.jsonl').open('a') as f:
                f.write(json.dumps(record, allow_nan=False) + '\n')
            if validation_rows:
                write_json(run / f'logs/validation_epoch{epoch:04d}.json', validation_rows)
            payload = {'format_version': 1, 'epoch': epoch, 'model': model.state_dict(),
                'latent': latents.state_dict(), 'latent_keys': dataset.latent_keys,
                'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(), 'scaler': scaler.state_dict(),
                'config': cfg, 'normalizer': normalizer.state_dict(), 'split_sha256': audit['split_sha256'],
                'rng': rng_state(), 'best_validation_mae': best, 'best_epoch': best_epoch,
                'monitor_best': monitor_best, 'bad_checks': bad_checks, 'train_mae': total/count,
                'consecutive_amp_overflows': consecutive_overflows,
                'validation_mae': value}
            save_checkpoint(run / 'checkpoints/last.pt', payload)
            if is_best: save_checkpoint(run / 'checkpoints/best.pt', payload)
            if epoch % cfg['train']['save_every'] == 0:
                save_checkpoint(run / f'checkpoints/epoch{epoch:04d}.pt', payload)
            print(f'epoch={epoch} train_mae={total/count:.6f} validation_mae={value}', flush=True)
            update_run(run, last_epoch=epoch, best_epoch=best_epoch, best_validation_mae=best if best_epoch else None)
            if bad_checks >= cfg['train']['patience']:
                stop_reason = 'early_stopping'; break
        summary = {'run_dir': str(run), 'last_epoch': epoch, 'best_epoch': best_epoch,
            'best_validation_mae': best, 'stop_reason': stop_reason,
            'checkpoint_best': str(run / 'checkpoints/best.pt'), 'checkpoint_last': str(run / 'checkpoints/last.pt')}
        write_json(run / 'summary.json', summary)
        update_run(run, status='completed', completed=timestamp(), stop_reason=stop_reason)
        return summary
    except BaseException as exc:
        update_run(run, status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed',
            ended=timestamp(), error=repr(exc)); raise
